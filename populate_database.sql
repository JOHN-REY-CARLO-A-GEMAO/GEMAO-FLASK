-- Database Population Script
-- This script populates the gemao_db with sample data for testing

USE gemao_db;

-- Insert sample users
INSERT IGNORE INTO users (firstname, lastname, email, username, password, role, is_active) VALUES
('Naruto', 'Uzumaki', 'naruto@leafvillage.com', 'naruto', 'pbkdf2:sha256:260000$8gHb2qL9vX6sW3zR$7f8K9nM2pQ4rS6tU1vW3xY5zZ8cB2dE4fG6hI8jK0l', 'user', TRUE),
('Sasuke', 'Uchiha', 'sasuke@leafvillage.com', 'sasuke', 'pbkdf2:sha256:260000$9gHc3qM9wY7tX4zS$8f9L0nM3qQ5rS6tU2vW3xY5zZ8cB2dE4fG6hI8jK0l', 'user', TRUE),
('Sakura', 'Haruno', 'sakura@leafvillage.com', 'sakura', 'pbkdf2:sha256:260000$aHd4qN0xZ8uW5zT$9g0M1nO4rS6tU3vW4xY6aA9bD3eF5hI7jK9lM2nQ4', 'user', TRUE),
('Kakashi', 'Hatake', 'kakashi@leafvillage.com', 'kakashi', 'pbkdf2:sha256:260000$bIe5rO1yA9vX6zS$0h1N2oP5qS7tU4vW5xY7bB0cD3eF6hI8jK0lM2nQ4', 'user', TRUE),
('Hinata', 'Hyuga', 'hinata@leafvillage.com', 'hinata', 'pbkdf2:sha256:260000$cJf6sP2zB0wY7tU$1i2O3pQ6rS8tU5vW6xY8cC0dE4fG7hI9jK0lM2nQ4', 'user', TRUE),
('Shikamaru', 'Nara', 'shikamaru@leafvillage.com', 'shikamaru', 'pbkdf2:sha256:260000$dKg7tQ3xC1xZ8vW$2j3P4rS7tU6vW7xY9dD0eF5hI8jK0lM2nQ4O6pR8', 'user', TRUE),
('Choji', 'Akimichi', 'choji@leafvillage.com', 'choji', 'pbkdf2:sha256:260000$eLh8uR4yD2yA9wX$3k4Q5sS8tU7vW8xY0eE6fG9hI2jK0lM2nQ4O6pR8', 'user', TRUE),
('Ino', 'Yamanaka', 'ino@leafvillage.com', 'ino', 'pbkdf2:sha256:260000$fMi9vS5zE3zB0xC$4l5R6tS9tU8vW9xY1fF7hG2jK3mN0oQ4O6pR8sT9', 'user', TRUE),
('Rock', 'Lee', 'rocklee@leafvillage.com', 'rocklee', 'pbkdf2:sha256:260000$gNj0wT6aF4xC1yD$5m6S7tU0vW0xY2gG8hI3jK4mN1oP5rS7tU9vW1xY3', 'user', TRUE),
('Tenten', 'Unknown', 'tenten@leafvillage.com', 'tenten', 'pbkdf2:sha256:260000$hOk1xU7bG5yD2zE$6n7T8uS1vW1xY3hH9iK4mN2oQ6rS8tU0vW2xY4', 'user', TRUE);

-- Insert user profiles
INSERT IGNORE INTO user_profiles (user_id, middlename, birthdate, age, contact_number, dream_job) VALUES
(1, 'Bolt', '1999-10-10', 24, '09123456789', 'Hokage'),
(2, 'Cold', '1999-07-23', 24, '09123456788', 'Revolutionary Leader'),
(3, 'Cherry', '1999-03-28', 24, '09123456787', 'Medical Ninja Chief'),
(4, 'Copy', '1979-09-15', 44, '09123456786', 'Sixth Hokage'),
(5, 'Gentle', '1999-12-27', 24, '09123456785', 'Head of Hyuga Clan'),
(6, 'Shadow', '1999-09-22', 24, '09123456784', 'Strategic Advisor'),
(7, 'Butterfly', '1999-05-01', 24, '09123456783', 'Restaurant Owner'),
(8, 'Mind', '1999-09-23', 24, '09123456782', 'Florist Shop Owner'),
(9, 'Green', '1999-11-27', 24, '09123456781', 'Greatest Taijutsu Master'),
(10, 'Weapon', '1999-03-09', 24, '09123456780', 'Weapons Master');

-- Insert games
INSERT IGNORE INTO games (name, description, file_path, image_path) VALUES
('Ninja Adventure', 'A thrilling ninja adventure game where you train to become the ultimate warrior', '/games/ninja_adventure.py', '/static/images/ninja_game.jpg'),
('Chunin Exam Challenge', 'Test your skills in the challenging Chunin examination', '/games/chunin_exam.py', '/static/images/chunin_exam.jpg'),
('Rasengan Training', 'Master the art of Rasengan in this training simulation', '/games/rasengan_training.py', '/static/images/rasengan.jpg'),
('Sharingan Battle', 'Battle against powerful Uchiha clan members', '/games/sharingan_battle.py', '/static/images/sharingan.jpg'),
('Leaf Village Defense', 'Defend the Hidden Leaf Village from enemy attacks', '/games/leaf_defense.py', '/static/images/leaf_village.jpg');

-- Insert game access (all users have access to all games)
INSERT IGNORE INTO game_access (user_id, game_id, is_allowed) VALUES
(1, 1, TRUE), (1, 2, TRUE), (1, 3, TRUE), (1, 4, TRUE), (1, 5, TRUE),
(2, 1, TRUE), (2, 2, TRUE), (2, 3, TRUE), (2, 4, TRUE), (2, 5, TRUE),
(3, 1, TRUE), (3, 2, TRUE), (3, 3, TRUE), (3, 4, TRUE), (3, 5, TRUE),
(4, 1, TRUE), (4, 2, TRUE), (4, 3, TRUE), (4, 4, TRUE), (4, 5, TRUE),
(5, 1, TRUE), (5, 2, TRUE), (5, 3, TRUE), (5, 4, TRUE), (5, 5, TRUE),
(6, 1, TRUE), (6, 2, TRUE), (6, 3, TRUE), (6, 4, TRUE), (6, 5, TRUE),
(7, 1, TRUE), (7, 2, TRUE), (7, 3, TRUE), (7, 4, TRUE), (7, 5, TRUE),
(8, 1, TRUE), (8, 2, TRUE), (8, 3, TRUE), (8, 4, TRUE), (8, 5, TRUE),
(9, 1, TRUE), (9, 2, TRUE), (9, 3, TRUE), (9, 4, TRUE), (9, 5, TRUE),
(10, 1, TRUE), (10, 2, TRUE), (10, 3, TRUE), (10, 4, TRUE), (10, 5, TRUE);

-- Insert sample leaderboard scores
INSERT IGNORE INTO leaderboard_scores (user_id, game_id, score_value, achieved_at, is_valid, session_id, playtime_seconds, difficulty_level, additional_metrics) VALUES
-- Ninja Adventure scores
(1, 1, 98500.00, '2024-01-15 10:30:00', TRUE, 'sess_001', 1800, 'hard', '{"kills": 45, "deaths": 3, "accuracy": 89.5}'),
(2, 1, 94200.00, '2024-01-15 11:45:00', TRUE, 'sess_002', 1650, 'hard', '{"kills": 42, "deaths": 5, "accuracy": 87.2}'),
(3, 1, 87800.00, '2024-01-15 14:20:00', TRUE, 'sess_003', 1920, 'medium', '{"kills": 38, "deaths": 7, "accuracy": 82.1}'),
(4, 1, 96500.00, '2024-01-15 16:10:00', TRUE, 'sess_004', 1740, 'hard', '{"kills": 44, "deaths": 4, "accuracy": 88.9}'),
(5, 1, 82300.00, '2024-01-15 17:30:00', TRUE, 'sess_005', 2100, 'medium', '{"kills": 35, "deaths": 9, "accuracy": 79.3}'),

-- Chunin Exam Challenge scores
(2, 2, 89200.00, '2024-01-16 09:15:00', TRUE, 'sess_006', 2400, 'expert', '{"questions_correct": 28, "time_bonus": 1500, "hints_used": 2}'),
(4, 2, 93400.00, '2024-01-16 10:30:00', TRUE, 'sess_007', 2250, 'expert', '{"questions_correct": 30, "time_bonus": 1800, "hints_used": 1}'),
(6, 2, 87600.00, '2024-01-16 13:45:00', TRUE, 'sess_008', 2580, 'hard', '{"questions_correct": 27, "time_bonus": 1200, "hints_used": 3}'),
(1, 2, 91800.00, '2024-01-16 15:20:00', TRUE, 'sess_009', 2340, 'expert', '{"questions_correct": 29, "time_bonus": 1650, "hints_used": 2}'),
(3, 2, 84500.00, '2024-01-16 16:40:00', TRUE, 'sess_010', 2720, 'hard', '{"questions_correct": 25, "time_bonus": 1000, "hints_used": 4}'),

-- Rasengan Training scores
(1, 3, 96800.00, '2024-01-17 08:00:00', TRUE, 'sess_011', 1500, 'hard', '{"rasengan_power": 95, "control_score": 92, "attempts": 15}'),
(4, 3, 98200.00, '2024-01-17 09:30:00', TRUE, 'sess_012', 1380, 'hard', '{"rasengan_power": 98, "control_score": 96, "attempts": 12}'),
(2, 3, 94500.00, '2024-01-17 11:15:00', TRUE, 'sess_013', 1620, 'hard', '{"rasengan_power": 93, "control_score": 90, "attempts": 18}'),
(7, 3, 89700.00, '2024-01-17 14:00:00', TRUE, 'sess_014', 1860, 'medium', '{"rasengan_power": 87, "control_score": 85, "attempts": 22}'),
(9, 3, 92300.00, '2024-01-17 15:45:00', TRUE, 'sess_015', 1710, 'hard', '{"rasengan_power": 91, "control_score": 88, "attempts": 16}'),

-- Sharingan Battle scores
(2, 4, 95600.00, '2024-01-18 10:00:00', TRUE, 'sess_016', 1950, 'expert', '{"sharingan_activated": TRUE, "victories": 12, "defeats": 2}'),
(1, 4, 93400.00, '2024-01-18 11:30:00', TRUE, 'sess_017', 2100, 'expert', '{"sharingan_activated": TRUE, "victories": 11, "defeats": 3}'),
(8, 4, 87900.00, '2024-01-18 13:15:00', TRUE, 'sess_018', 2280, 'hard', '{"sharingan_activated": FALSE, "victories": 9, "defeats": 5}'),
(4, 4, 97100.00, '2024-01-18 15:00:00', TRUE, 'sess_019', 1830, 'expert', '{"sharingan_activated": TRUE, "victories": 13, "defeats": 1}'),
(5, 4, 89800.00, '2024-01-18 16:45:00', TRUE, 'sess_020', 2160, 'hard', '{"sharingan_activated": FALSE, "victories": 10, "defeats": 4}'),

-- Leaf Village Defense scores
(4, 1, 99200.00, '2024-01-19 08:30:00', TRUE, 'sess_021', 2700, 'expert', '{"waves_survived": 15, "enemies_defeated": 287, "buildings_saved": 8}'),
(1, 1, 97800.00, '2024-01-19 10:15:00', TRUE, 'sess_022', 2850, 'expert', '{"waves_survived": 14, "enemies_defeated": 265, "buildings_saved": 7}'),
(6, 1, 92400.00, '2024-01-19 12:00:00', TRUE, 'sess_023', 3000, 'hard', '{"waves_survived": 12, "enemies_defeated": 234, "buildings_saved": 6}'),
(9, 1, 95600.00, '2024-01-19 14:30:00', TRUE, 'sess_024', 2760, 'expert', '{"waves_survived": 13, "enemies_defeated": 251, "buildings_saved": 7}'),
(3, 1, 88900.00, '2024-01-19 16:15:00', TRUE, 'sess_025', 3120, 'hard', '{"waves_survived": 11, "enemies_defeated": 198, "buildings_saved": 5}');

-- Insert user personal bests (calculated from scores above)
INSERT IGNORE INTO user_personal_bests (user_id, game_id, best_score, best_rank, achieved_at, total_plays, average_score, last_played_at) VALUES
(1, 1, 98500.00, 1, '2024-01-15 10:30:00', 3, 92433.33, '2024-01-19 10:15:00'),
(2, 1, 94200.00, 2, '2024-01-15 11:45:00', 2, 94900.00, '2024-01-18 10:00:00'),
(3, 1, 87800.00, 4, '2024-01-15 14:20:00', 3, 87066.67, '2024-01-19 16:15:00'),
(4, 1, 99200.00, 1, '2024-01-19 08:30:00', 4, 96550.00, '2024-01-19 08:30:00'),
(5, 1, 82300.00, 5, '2024-01-15 17:30:00', 2, 86050.00, '2024-01-18 16:45:00'),
(6, 1, 92400.00, 3, '2024-01-19 12:00:00', 1, 92400.00, '2024-01-19 12:00:00'),
(9, 1, 95600.00, 2, '2024-01-19 14:30:00', 1, 95600.00, '2024-01-19 14:30:00'),

(1, 2, 91800.00, 3, '2024-01-16 15:20:00', 1, 91800.00, '2024-01-16 15:20:00'),
(2, 2, 89200.00, 4, '2024-01-16 09:15:00', 1, 89200.00, '2024-01-16 09:15:00'),
(3, 2, 84500.00, 5, '2024-01-16 16:40:00', 1, 84500.00, '2024-01-16 16:40:00'),
(4, 2, 93400.00, 1, '2024-01-16 10:30:00', 1, 93400.00, '2024-01-16 10:30:00'),
(6, 2, 87600.00, 3, '2024-01-16 13:45:00', 1, 87600.00, '2024-01-16 13:45:00'),

(1, 3, 96800.00, 2, '2024-01-17 08:00:00', 1, 96800.00, '2024-01-17 08:00:00'),
(2, 3, 94500.00, 3, '2024-01-17 11:15:00', 1, 94500.00, '2024-01-17 11:15:00'),
(4, 3, 98200.00, 1, '2024-01-17 09:30:00', 1, 98200.00, '2024-01-17 09:30:00'),
(7, 3, 89700.00, 4, '2024-01-17 14:00:00', 1, 89700.00, '2024-01-17 14:00:00'),
(9, 3, 92300.00, 3, '2024-01-17 15:45:00', 1, 92300.00, '2024-01-17 15:45:00'),

(1, 4, 93400.00, 2, '2024-01-18 11:30:00', 1, 93400.00, '2024-01-18 11:30:00'),
(2, 4, 95600.00, 2, '2024-01-18 10:00:00', 1, 95600.00, '2024-01-18 10:00:00'),
(4, 4, 97100.00, 1, '2024-01-18 15:00:00', 1, 97100.00, '2024-01-18 15:00:00'),
(5, 4, 89800.00, 4, '2024-01-18 16:45:00', 1, 89800.00, '2024-01-18 16:45:00'),
(8, 4, 87900.00, 5, '2024-01-18 13:15:00', 1, 87900.00, '2024-01-18 13:15:00');

-- Insert sample audit logs
INSERT IGNORE INTO audit_logs (actor_id, target_user_id, action, details, created_at) VALUES
(1, 2, 'USER_CREATED', 'Admin created user Sasuke Uchiha', '2024-01-15 09:00:00'),
(1, 3, 'USER_CREATED', 'Admin created user Sakura Haruno', '2024-01-15 09:05:00'),
(1, 4, 'USER_CREATED', 'Admin created user Kakashi Hatake', '2024-01-15 09:10:00'),
(1, 1, 'LOGIN_SUCCESS', 'User Naruto Uzumaki logged in', '2024-01-15 10:00:00'),
(2, 2, 'LOGIN_SUCCESS', 'User Sasuke Uchiha logged in', '2024-01-15 11:00:00'),
(1, 1, 'SCORE_SUBMITTED', 'Naruto submitted score 98500 in Ninja Adventure', '2024-01-15 10:30:00'),
(2, 2, 'SCORE_SUBMITTED', 'Sasuke submitted score 94200 in Ninja Adventure', '2024-01-15 11:45:00'),
(4, 4, 'SCORE_SUBMITTED', 'Kakashi submitted score 96500 in Ninja Adventure', '2024-01-15 16:10:00'),
(1, 1, 'ACHIEVEMENT_UNLOCKED', 'Naruto unlocked "First Victory" achievement', '2024-01-15 10:35:00'),
(2, 2, 'ACHIEVEMENT_UNLOCKED', 'Sasuke unlocked "Sharpshooter" achievement', '2024-01-15 11:50:00');

-- Update leaderboard rankings cache (all_time)
INSERT IGNORE INTO leaderboard_rankings (game_id, user_id, rank_position, score_value, achieved_at, time_period, period_start, period_end, last_updated) VALUES
-- Ninja Adventure
(1, 4, 1, 99200.00, '2024-01-19 08:30:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-19 08:30:00'),
(1, 1, 2, 98500.00, '2024-01-15 10:30:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-15 10:30:00'),
(1, 9, 3, 95600.00, '2024-01-19 14:30:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-19 14:30:00'),
(1, 6, 4, 92400.00, '2024-01-19 12:00:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-19 12:00:00'),
(1, 2, 5, 94200.00, '2024-01-15 11:45:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-15 11:45:00'),

-- Chunin Exam Challenge
(2, 4, 1, 93400.00, '2024-01-16 10:30:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-16 10:30:00'),
(2, 1, 2, 91800.00, '2024-01-16 15:20:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-16 15:20:00'),
(2, 6, 3, 87600.00, '2024-01-16 13:45:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-16 13:45:00'),
(2, 2, 4, 89200.00, '2024-01-16 09:15:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-16 09:15:00'),
(2, 3, 5, 84500.00, '2024-01-16 16:40:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-16 16:40:00'),

-- Rasengan Training
(3, 4, 1, 98200.00, '2024-01-17 09:30:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-17 09:30:00'),
(3, 1, 2, 96800.00, '2024-01-17 08:00:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-17 08:00:00'),
(3, 2, 3, 94500.00, '2024-01-17 11:15:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-17 11:15:00'),
(3, 9, 4, 92300.00, '2024-01-17 15:45:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-17 15:45:00'),
(3, 7, 5, 89700.00, '2024-01-17 14:00:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-17 14:00:00'),

-- Sharingan Battle
(4, 4, 1, 97100.00, '2024-01-18 15:00:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-18 15:00:00'),
(4, 2, 2, 95600.00, '2024-01-18 10:00:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-18 10:00:00'),
(4, 1, 3, 93400.00, '2024-01-18 11:30:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-18 11:30:00'),
(4, 5, 4, 89800.00, '2024-01-18 16:45:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-18 16:45:00'),
(4, 8, 5, 87900.00, '2024-01-18 13:15:00', 'all_time', '2024-01-01 00:00:00', '2099-12-31 23:59:59', '2024-01-18 13:15:00');

-- Display summary of populated data
SELECT 'Database populated successfully!' as status;
SELECT COUNT(*) as total_users FROM users;
SELECT COUNT(*) as total_games FROM games;
SELECT COUNT(*) as total_scores FROM leaderboard_scores;
SELECT COUNT(*) as total_personal_bests FROM user_personal_bests;
SELECT COUNT(*) as total_audit_logs FROM audit_logs;
SELECT COUNT(*) as total_rankings FROM leaderboard_rankings;
