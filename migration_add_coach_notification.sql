-- Migration: Add Coach Assignment and Notification Tracking
-- Date: 2025-12-05
-- Description: Adds coach_id and last_notification_sent columns to assessments table

-- Add coach_id column (references users table)
ALTER TABLE assessments ADD COLUMN coach_id TEXT REFERENCES users(user_id);

-- Add last_notification_sent column (for rate limiting)
ALTER TABLE assessments ADD COLUMN last_notification_sent TEXT;

-- Optional: If you want to assign a default coach to existing assessments
-- Uncomment and modify the line below to set a default coach
-- UPDATE assessments SET coach_id = (SELECT user_id FROM users WHERE role = 'admin' LIMIT 1) WHERE coach_id IS NULL;

-- Verify the migration
SELECT assessment_id, assessment_name, owner_id, coach_id, last_notification_sent
FROM assessments
LIMIT 5;
