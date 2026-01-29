/**
 * Overlapping Assessments View
 * Handles checkbox toggling and opacity calculation for stacked wheel visualization
 */
document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.assessment-checkbox');
    const selectAllCheckbox = document.getElementById('select-all-assessments');
    const wheelsStack = document.getElementById('wheels-stack');
    const wheelsPlaceholder = document.getElementById('wheels-placeholder');
    const selectedCountEl = document.getElementById('selected-count');
    const opacityValueEl = document.getElementById('opacity-value');

    // Exit early if not on overlapping assessments page
    if (!wheelsStack || !checkboxes.length) {
        return;
    }

    // Store loaded wheel SVGs
    const loadedWheels = new Map();

    // Update the visualization when checkboxes change
    function updateVisualization() {
        const selectedCheckboxes = document.querySelectorAll('.assessment-checkbox:checked');
        const selectedCount = selectedCheckboxes.length;

        // Update counters
        selectedCountEl.textContent = selectedCount;

        if (selectedCount === 0) {
            wheelsPlaceholder.style.display = 'block';
            wheelsStack.style.display = 'none';
            opacityValueEl.textContent = '0%';
            return;
        }

        // Calculate opacity so overlapping areas combine to ~95% opacity
        // Formula: opacity = 1 - (1 - target)^(1/n)
        // This ensures that when n layers overlap, combined opacity approaches target
        var targetCombinedOpacity = 0.95;
        var opacity = 1 - Math.pow(1 - targetCombinedOpacity, 1 / selectedCount);
        opacityValueEl.textContent = Math.round(opacity * 100) + '%';

        wheelsPlaceholder.style.display = 'none';
        wheelsStack.style.display = 'block';

        // Clear existing wheels
        wheelsStack.innerHTML = '';

        // Load and display selected wheels
        selectedCheckboxes.forEach(function(checkbox) {
            const assessmentId = checkbox.dataset.assessmentId;
            const assessmentName = checkbox.dataset.assessmentName;

            // Create layer container
            const layer = document.createElement('div');
            layer.className = 'wheel-layer';
            layer.style.opacity = opacity;
            layer.dataset.assessmentId = assessmentId;
            layer.title = assessmentName;

            // Check if already loaded
            if (loadedWheels.has(assessmentId)) {
                layer.innerHTML = loadedWheels.get(assessmentId);
                wheelsStack.appendChild(layer);
            } else {
                // Fetch the wheel SVG
                layer.innerHTML = '<div class="has-text-centered py-6">Loading...</div>';
                wheelsStack.appendChild(layer);

                fetch('/dashboard/assessments/overlapping/wheel/' + assessmentId)
                    .then(function(response) {
                        return response.text();
                    })
                    .then(function(svgContent) {
                        loadedWheels.set(assessmentId, svgContent);
                        // Only update if still selected
                        const stillSelected = document.querySelector(
                            '.assessment-checkbox[data-assessment-id="' + assessmentId + '"]:checked'
                        );
                        if (stillSelected) {
                            layer.innerHTML = svgContent;
                        }
                    })
                    .catch(function(error) {
                        console.error('Error loading wheel:', error);
                        layer.innerHTML = '<div class="has-text-danger">Failed to load</div>';
                    });
            }
        });
    }

    // Update select all checkbox state
    function updateSelectAllState() {
        const allChecked = Array.from(checkboxes).every(function(cb) {
            return cb.checked;
        });
        const someChecked = Array.from(checkboxes).some(function(cb) {
            return cb.checked;
        });
        selectAllCheckbox.checked = allChecked;
        selectAllCheckbox.indeterminate = someChecked && !allChecked;
    }

    // Add event listeners to checkboxes
    checkboxes.forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            updateVisualization();
            updateSelectAllState();
        });
    });

    // Select all functionality
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            checkboxes.forEach(function(checkbox) {
                checkbox.checked = isChecked;
            });
            updateVisualization();
        });
    }
});
