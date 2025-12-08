-- Populate Game Categories
-- This script adds sample categories and associates them with existing games

USE gemao_db;

-- Insert sample game categories
INSERT IGNORE INTO game_categories (name, description) VALUES
('Puzzle', 'Brain-teasing games that challenge your problem-solving skills'),
('Action', 'Fast-paced games that test your reflexes and coordination'),
('Strategy', 'Games that require planning, tactical thinking, and resource management'),
('Adventure', 'Exploration-based games with immersive storylines'),
('Arcade', 'Classic-style games with simple mechanics and high replay value'),
('Educational', 'Games designed to teach and reinforce various skills'),
('Multiplayer', 'Games that support multiple players competing or cooperating'),
('Naruto-Themed', 'Games inspired by the popular Naruto anime series');

-- Associate existing games with categories
-- Note: Adjust game_id values based on your actual games table

-- Game ID 1 - Assuming it's a puzzle game
INSERT IGNORE INTO game_category_association (game_id, category_id) 
SELECT 1, id FROM game_categories WHERE name = 'Puzzle';

-- Game ID 2 - Assuming it's an action game  
INSERT IGNORE INTO game_category_association (game_id, category_id)
SELECT 2, id FROM game_categories WHERE name = 'Action';

-- Game ID 3 - Assuming it's a strategy game
INSERT IGNORE INTO game_category_association (game_id, category_id)
SELECT 3, id FROM game_categories WHERE name = 'Strategy';

-- Add Naruto theme to all games (since this seems to be a Naruto-themed app)
INSERT IGNORE INTO game_category_association (game_id, category_id)
SELECT g.id, gc.id FROM games g CROSS JOIN game_categories gc 
WHERE gc.name = 'Naruto-Themed' AND g.id IN (1, 2, 3);

-- Display results
SELECT 
    g.name as game_name,
    gc.name as category_name,
    gc.description as category_description
FROM games g
JOIN game_category_association gca ON g.id = gca.game_id
JOIN game_categories gc ON gca.category_id = gc.id
ORDER BY g.name, gc.name;
