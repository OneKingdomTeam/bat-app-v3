#!/usr/bin/env python3
"""
Script to update SVG wheel templates with disabled segment functionality.
Updates all 4 wheel SVG files to add enabled/disabled state handling.
"""

import re
from pathlib import Path

def update_svg_category(content: str, category_num: int) -> str:
    """Update a single category in the SVG content"""
    category_id = f"{category_num:02d}"

    # Pattern to match the category <g> opening tag
    old_g_pattern = (
        rf'(<g class="category category-{category_id})'
        rf'( \{{%[^}]+\}})?'  # optional active class
        rf'(" data-category_name="\{{{{ wheel\.category_name_{category_id} \}}\}}")'
    )

    new_g_replacement = (
        rf'\1\2'
        rf' \{{%% if not wheel.category_{category_id}_enabled %%}}disabled\{{%% endif %%}}\3'
        rf'\n   data-enabled="\{{{{ wheel.category_{category_id}_enabled \}}}}"'
    )

    content = re.sub(old_g_pattern, new_g_replacement, content)

    # Find and update the clickable overlay path (the one with hx-get)
    # Pattern to match the transparent overlay path with HTMX attributes
    overlay_pattern = (
        rf'(<path d="[^"]*"\s+'
        rf'fill="rgba\(255,255,255,0\)"\s*'
        rf')(hx-get="[^"]*"\s+'
        rf'hx-push-url="true"\s+'
        rf'hx-target="[^"]*"\s+'
        rf'hx-select="[^"]*"\s+'
        rf'hx-swap="[^"]*"\s*)'
        rf'(/>\s*</g>)'
    )

    # Check if this is within our category by looking for context around it
    # We'll need to find sections that belong to category-{category_id}

    # Split content by category sections
    category_start = f'<g class="category category-{category_id}'
    category_end_pattern = rf'</g>\s*(?=<g class="category category-\d{{2}}|<text)'

    # Find the start of this category
    cat_start_idx = content.find(category_start)
    if cat_start_idx == -1:
        return content

    # Find the end of this category (next category or text element)
    cat_end_match = re.search(category_end_pattern, content[cat_start_idx:])
    if not cat_end_match:
        # Try to find just </g> at the end of file
        next_g = content.find('</g>', cat_start_idx + 100)
        if next_g != -1:
            cat_end_idx = next_g + 4
        else:
            return content
    else:
        cat_end_idx = cat_start_idx + cat_end_match.end()

    category_section = content[cat_start_idx:cat_end_idx]

    # Update the overlay path in this section
    updated_section = re.sub(
        overlay_pattern,
        rf'\1{{% if wheel.category_{category_id}_enabled %}}\n        \2\n        {{% else %}}\n        style="pointer-events: none;"\n        {{% endif %}}\3\n    {{% if not wheel.category_{category_id}_enabled %}}\n    <path d="\2" fill="rgba(128, 128, 128, 0.5)" style="pointer-events: none;" class="disabled-overlay"/>\n    {{% endif %}}\3',
        category_section
    )

    # If that didn't work, try a simpler approach
    if updated_section == category_section:
        # Look for the last path element before </g>
        last_path_pattern = r'(<path d="[^"]*"\s+fill="rgba\(255,255,255,0\)"[^>]*)(/>)\s*(</g>)'

        def replace_overlay(match):
            path_start = match.group(1)
            path_end = match.group(2)
            g_end = match.group(3)

            # Check if it already has hx-get
            if 'hx-get' in path_start:
                # Extract hx attributes
                hx_attrs_match = re.search(
                    r'(hx-get="[^"]*"\s+hx-push-url="true"\s+hx-target="[^"]*"\s+hx-select="[^"]*"\s+hx-swap="[^"]*")',
                    path_start
                )
                if hx_attrs_match:
                    hx_attrs = hx_attrs_match.group(1)
                    # Remove hx attributes from path_start
                    path_without_hx = path_start.replace(hx_attrs, '').strip()

                    result = (
                        f'{path_without_hx}\n'
                        f'        {{% if wheel.category_{category_id}_enabled %}}\n'
                        f'        {hx_attrs}\n'
                        f'        {{% else %}}\n'
                        f'        style="pointer-events: none;"\n'
                        f'        {{% endif %}}\n'
                        f'        {path_end}\n'
                        f'    {{% if not wheel.category_{category_id}_enabled %}}\n'
                        f'    <path d="M0,0" fill="rgba(128, 128, 128, 0.5)" style="pointer-events: none;" class="disabled-overlay"/>\n'
                        f'    {{% endif %}}\n'
                        f'    {g_end}'
                    )
                    return result

            return match.group(0)

        updated_section = re.sub(last_path_pattern, replace_overlay, category_section, count=1)

    # Replace the section in the original content
    content = content[:cat_start_idx] + updated_section + content[cat_end_idx:]

    return content


def process_svg_file(file_path: Path) -> bool:
    """Process a single SVG file"""
    print(f"Processing {file_path.name}...")

    try:
        content = file_path.read_text()
        original_content = content

        # Update all 13 categories (00-12)
        for i in range(13):
            content = update_svg_category(content, i)

        if content != original_content:
            # Backup original file
            backup_path = file_path.with_suffix('.svg.bak')
            backup_path.write_text(original_content)
            print(f"  Created backup: {backup_path.name}")

            # Write updated content
            file_path.write_text(content)
            print(f"  ✓ Updated {file_path.name}")
            return True
        else:
            print(f"  No changes needed for {file_path.name}")
            return False
    except Exception as e:
        print(f"  ✗ Error processing {file_path.name}: {e}")
        return False


def main():
    """Main function to update all SVG wheel templates"""
    wheel_dir = Path("/home/claude/coding/bat-app-v3/app/template/jinja/wheel")

    svg_files = [
        "wheel.svg",
        "wheel-app.svg",
        "wheel-review.svg",
        "wheel-report.svg"
    ]

    print("SVG Wheel Template Updater")
    print("=" * 50)
    print()

    for svg_file in svg_files:
        file_path = wheel_dir / svg_file
        if file_path.exists():
            process_svg_file(file_path)
        else:
            print(f"✗ File not found: {svg_file}")
        print()

    print("=" * 50)
    print("Done!")


if __name__ == "__main__":
    main()
