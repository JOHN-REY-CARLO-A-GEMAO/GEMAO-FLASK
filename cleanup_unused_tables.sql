-- SQL Script to Drop Unused Database Tables
-- Run this script to remove tables that are not implemented in the frontend

-- WARNING: This will permanently delete data. Make sure to backup your database first!

-- Method 1: Try disabling foreign key checks (may not work in all phpMyAdmin versions)
SET FOREIGN_KEY_CHECKS = 0;

-- Method 2: Drop tables one by one with error handling
-- If the above doesn't work, run these commands individually in phpMyAdmin

-- Drop tables in any order since foreign key checks are disabled
DROP TABLE IF EXISTS scores;
DROP TABLE IF EXISTS feature_progress;
DROP TABLE IF EXISTS features;
DROP TABLE IF EXISTS api_keys;
DROP TABLE IF EXISTS badges;
DROP TABLE IF EXISTS click_events;
DROP TABLE IF EXISTS store_items;
DROP TABLE IF EXISTS streaks;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- 4. Clean up any remaining references in code
-- The following tables are kept as they have frontend implementations:
-- - users, user_sessions (core authentication)
-- - games, game_access (game system)
-- - leaderboard_scores, leaderboard_rankings (leaderboard)
-- - blog_posts, content_versions (blog)
-- - audit_logs (security)
-- - game_categories, game_category_association (category management)
-- - notification_preferences (user preferences)
-- - points_transactions, user_points (points system)
-- - user_personal_bests (personal records)
-- - otp_verification (security)
-- - score_validation_rules (admin)

SELECT 'Unused tables dropped successfully' as status;
