-- Leaderboard System Database Schema
-- This file extends the existing gemao_db with leaderboard functionality

USE gemao_db;

-- 7. Leaderboard Scores Table
CREATE TABLE IF NOT EXISTS leaderboard_scores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    game_id INT NOT NULL,
    score_value DECIMAL(15,2) NOT NULL,
    rank_position INT GENERATED ALWAYS AS (
        DENSE_RANK() OVER (PARTITION BY game_id ORDER BY score_value DESC)
    ) STORED,
    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_valid BOOLEAN DEFAULT TRUE,
    validation_hash VARCHAR(64),
    session_id VARCHAR(100),
    playtime_seconds INT DEFAULT 0,
    difficulty_level ENUM('easy', 'medium', 'hard', 'expert') DEFAULT 'medium',
    additional_metrics JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
    INDEX idx_game_score (game_id, score_value DESC),
    INDEX idx_user_game (user_id, game_id),
    INDEX idx_achieved_at (achieved_at),
    INDEX idx_rank_position (rank_position)
);

-- 8. Leaderboard Rankings Cache Table (for performance)
CREATE TABLE IF NOT EXISTS leaderboard_rankings (
    game_id INT,
    user_id INT,
    rank_position INT,
    score_value DECIMAL(15,2),
    achieved_at TIMESTAMP,
    time_period ENUM('daily', 'weekly', 'all_time') DEFAULT 'all_time',
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (game_id, user_id, time_period),
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_game_period (game_id, time_period, rank_position),
    INDEX idx_period_updated (time_period, last_updated)
);

-- 9. Score Validation Rules Table
CREATE TABLE IF NOT EXISTS score_validation_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    game_id INT,
    max_score DECIMAL(15,2),
    min_score DECIMAL(15,2) DEFAULT 0,
    max_playtime_seconds INT,
    score_multiplier DECIMAL(5,2) DEFAULT 1.0,
    validation_rules JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);

-- 10. User Personal Bests Table
CREATE TABLE IF NOT EXISTS user_personal_bests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    game_id INT NOT NULL,
    best_score DECIMAL(15,2) NOT NULL,
    best_rank INT,
    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_plays INT DEFAULT 1,
    average_score DECIMAL(15,2),
    last_played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_game (user_id, game_id),
    INDEX idx_user_best (user_id, best_score DESC)
);

-- Insert sample validation rules for existing games
INSERT IGNORE INTO score_validation_rules (game_id, max_score, min_score, max_playtime_seconds, validation_rules) 
VALUES 
(1, 999999.99, 0, 3600, '{"max_score_per_minute": 1000, "require_session_validation": true}'),
(2, 999999.99, 0, 3600, '{"max_score_per_minute": 1000, "require_session_validation": true}'),
(3, 999999.99, 0, 3600, '{"max_score_per_minute": 1000, "require_session_validation": true}');
