# Additional Changes - Coach Display and Inline Editing

## Overview
These additional changes fix the owner selector issue and add coach display/editing to assessment list views.

## Changes Made

### 1. Fixed Owner Selector Issue

**Problem:** Owner selector was only showing coaches, but it should show ALL users since any user can be the owner (fill out) an assessment.

**Files Modified:**
- `app/web/dashboard/assessments.py` - Added `users` list alongside `coaches` list
- `app/template/jinja/dashboard/assessment-create.html` - Updated owner dropdown to use `users` instead of `coaches`

**Details:**
- Coach dropdown: Shows only admins/coaches (for guiding the assessment)
- Owner dropdown: Shows all users (for who will fill out the assessment)

### 2. Added Coach Display to Assessment Lists

**Files Modified:**
- `app/template/jinja/dashboard/assessments.html` - Added coach row with inline editing (for admins/coaches)
- `app/template/jinja/app/assessments.html` - Added read-only coach display (for users)

**Dashboard View (Admin/Coach):**
```html
<div class="coach-row is-clickable" hx-get="...">
    <span class="has-text-grey">Coach</span>
    <span class="has-text-weight-medium">{{ assessment.coach_name }} ✏️</span>
</div>
```

**App View (User):**
```html
<div class="is-flex is-justify-content-space-between">
    <span class="has-text-grey">Coach</span>
    <span class="has-text-weight-medium">{{ assessment.coach_name }}</span>
</div>
```

### 3. Added Inline Coach Editing Functionality

**New Model:**
- `app/model/assesment.py` - Added `AssessmentChangeCoach` model

**New Data Layer Function:**
- `app/data/assessment.py` - Added `change_coach()` function to update coach_id

**New Service Layer Function:**
- `app/service/assessment.py` - Added `change_coach()` with validation

**New Routes:**
- `GET /dashboard/assessments/change-coach/{assessment_id}` - Get coach change form
- `PUT /dashboard/assessments` (with AssessmentChangeCoach body) - Update coach

**New Template:**
- `app/template/jinja/dashboard/assessments-change-coach.html` - Inline editing form

## How Inline Coach Editing Works

1. **User clicks on coach name** (with ✏️ icon) in dashboard assessment list
2. **HTMX swaps the row** with a dropdown of available coaches
3. **User selects new coach** from dropdown
4. **On change event**, form automatically submits via HTMX
5. **Backend validates** coach role (admin/coach only)
6. **Page refreshes** showing updated coach name

This follows the exact same pattern as the existing owner inline editing functionality.

## Security Validation

Backend validation ensures:
- Only admins/coaches can change the coach assignment
- Selected coach must have admin or coach role
- Regular users cannot be assigned as coaches (even if HTML is modified)

## Display Logic

**Dashboard (Admins/Coaches):**
- Shows coach name with ✏️ icon for inline editing
- Shows "None" in italics if no coach assigned
- Clicking opens dropdown to change coach

**App (Users):**
- Shows coach name (read-only)
- Shows "None" in italics if no coach assigned
- No editing capability

## Testing

### Test Scenario 1: Assessment Creation
1. Navigate to `/dashboard/assessments/create`
2. Verify Coach dropdown shows only admin/coach users
3. Verify Owner dropdown shows ALL users
4. Create assessment and verify both fields saved correctly

### Test Scenario 2: Coach Display in Lists
1. Navigate to `/dashboard/assessments`
2. Verify coach name shows in assessment cards
3. Verify "None" shows for assessments without coach

### Test Scenario 3: Inline Coach Editing
1. Click on coach name (with ✏️)
2. Verify dropdown appears with available coaches
3. Select different coach
4. Verify auto-submit and page refresh
5. Verify coach updated correctly

### Test Scenario 4: User View
1. Login as regular user
2. Navigate to `/app/assessments`
3. Verify coach name displays (read-only)
4. No edit icon should appear

### Test Scenario 5: Backend Validation
1. Try to assign regular user as coach (modify HTML)
2. Verify backend rejects with InvalidCoachAssignment error
3. Only admin/coach role users can be assigned

## Summary of All Files Changed

### Models
- `app/model/assesment.py` - Added `AssessmentChangeCoach`

### Data Layer
- `app/data/assessment.py` - Added `change_coach()` function

### Service Layer
- `app/service/assessment.py` - Added `change_coach()` function with validation

### Routes
- `app/web/dashboard/assessments.py` - Added GET/PUT routes for coach change, fixed users list

### Templates (Modified)
- `app/template/jinja/dashboard/assessment-create.html` - Fixed owner dropdown
- `app/template/jinja/dashboard/assessments.html` - Added coach row with inline editing
- `app/template/jinja/app/assessments.html` - Added coach display

### Templates (New)
- `app/template/jinja/dashboard/assessments-change-coach.html` - Coach change form

## Total Additional Changes
- **3 files modified** (routes, 2 templates)
- **1 new template** created
- **3 new functions** added (model, data, service)
- **2 new routes** added
- **0 breaking changes**
