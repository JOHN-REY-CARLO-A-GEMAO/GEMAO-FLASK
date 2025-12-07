# Comprehensive Leaderboard System

A complete leaderboard system for tracking and displaying user scores across multiple games with advanced features including time-based rankings, score validation, and backup/recovery capabilities.

## Features

### Core Functionality
- **Score Tracking**: Store user scores with game-specific metrics
- **Dynamic Rankings**: Real-time ranking updates with position calculation
- **Multi-Game Support**: Separate leaderboards for each game
- **User Profiles**: Personal bests and score history

### Advanced Features
- **Time-Based Leaderboards**: Daily, weekly, and all-time rankings
- **Score Validation**: Anti-cheat mechanisms with configurable rules
- **Performance Optimization**: Caching system for fast queries
- **Pagination**: Efficient browsing through large score lists
- **User Comparison**: Side-by-side performance comparison
- **Backup & Recovery**: Automated backup and restore functionality

## Database Schema

### Core Tables
1. **leaderboard_scores** - Main score storage
2. **leaderboard_rankings** - Performance cache for rankings
3. **user_personal_bests** - User's best scores per game
4. **score_validation_rules** - Anti-cheat validation rules

### Key Fields
- User ID/username tracking
- Game ID/name association
- Score value with decimal precision
- Timestamp of achievement
- Additional game-specific metrics (JSON)
- Difficulty levels
- Playtime tracking
- Validation hashes

## API Endpoints

### Score Management
- `POST /api/leaderboard/scores` - Submit new score
- `GET /api/leaderboard/games/{id}/top` - Get top scores
- `GET /api/leaderboard/users/{id}/scores` - Get user scores
- `GET /api/leaderboard/users/{id}/personal-bests` - Get personal bests

### Rankings & Comparison
- `GET /api/leaderboard/games/{id}/rank/{user_id}` - Get user rank
- `POST /api/leaderboard/compare` - Compare multiple users
- `GET /api/leaderboard/games/{id}/stats` - Game statistics
- `GET /api/leaderboard/stats/global` - Global statistics

### Validation
- `POST /api/leaderboard/validate` - Validate score without submitting

## Frontend Pages

### Main Leaderboard (`/leaderboards/`)
- Game selection dropdown
- Time period filters (Daily/Weekly/All-Time)
- Difficulty level filtering
- Results per page options
- Real-time score updates
- Visual ranking indicators (Gold/Silver/Bronze medals)
- User comparison tool

### User Profiles (`/leaderboards/user/{id}`)
- Personal best scores
- Recent score history
- Performance statistics
- Achievement timeline

### Game-Specific Leaderboards (`/leaderboards/game/{id}`)
- Detailed game statistics
- Top player rankings
- User's current position
- Difficulty-specific rankings

## Installation & Setup

### 1. Database Setup
```sql
-- Run the leaderboard database schema
mysql -u username -p database_name < leaderboard_database.sql
```

### 2. Dependencies
The system uses existing Flask dependencies:
- Flask
- Flask-Login
- mysql-connector-python

### 3. Configuration
The leaderboard system is automatically registered in the Flask app through `__init__.py`.

## Usage Examples

### Submitting a Score
```javascript
fetch('/api/leaderboard/scores', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token
    },
    body: JSON.stringify({
        game_id: 1,
        score_value: 1500,
        playtime_seconds: 300,
        difficulty_level: 'medium',
        additional_metrics: {
            accuracy: 0.85,
            combo_count: 12
        }
    })
})
```

### Getting Top Scores
```javascript
fetch('/api/leaderboard/games/1/top?time_period=weekly&limit=25')
    .then(response => response.json())
    .then(data => console.log(data.scores));
```

### Comparing Users
```javascript
fetch('/api/leaderboard/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        user_ids: [1, 2, 3],
        game_id: 1,
        time_period: 'all_time'
    })
})
```

## Score Validation

### Built-in Validation Rules
- **Score Range**: Minimum/maximum score limits per game
- **Time Limits**: Maximum playtime validation
- **Score Rate**: Maximum score per minute to prevent cheating
- **Session Validation**: Hash-based score integrity

### Custom Validation Rules
Configure per-game validation rules in the `score_validation_rules` table:
```json
{
    "max_score_per_minute": 1000,
    "require_session_validation": true,
    "impossible_threshold": 999999,
    "custom_checks": {
        "min_accuracy": 0.1,
        "max_combo_multiplier": 5
    }
}
```

## Performance Optimization

### Caching System
- **Rankings Cache**: Pre-calculated rankings for fast queries
- **Time-Based Caching**: Separate caches for daily/weekly/all-time
- **Automatic Updates**: Cache updates on score submission

### Database Indexes
- Composite indexes on (game_id, score_value)
- User-game relationship indexes
- Time-based query indexes

## Backup & Recovery

### Automated Backups
```python
from MyFlaskapp.leaderboard_backup import LeaderboardBackup

# Create backup
backup = LeaderboardBackup()
result = backup.create_backup("full")

# Restore from backup
restore_result = backup.restore_backup("backup_file.json", "full")
```

### Export Options
- JSON format for full backups
- CSV export for data analysis
- Selective table exports

### Scheduled Maintenance
```python
from MyFlaskapp.leaderboard_backup import scheduled_backup, scheduled_maintenance

# Daily backup
scheduled_backup()

# Weekly maintenance
scheduled_maintenance()
```

## Security Features

### Anti-Cheat Measures
- Score validation with configurable rules
- Session-based hash verification
- Playtime consistency checks
- Suspicious score detection

### Access Control
- User authentication required for score submission
- Admin-only access to backup/restore functions
- CSRF protection on all forms

## Monitoring & Analytics

### Game Statistics
- Total plays and unique players
- Score distribution analysis
- Difficulty breakdown
- Daily/weekly activity tracking

### User Analytics
- Personal best tracking
- Performance trends
- Ranking history
- Playtime analysis

## Customization

### Visual Customization
- CSS classes for ranking medals
- Responsive design for mobile devices
- Theme-compatible styling
- Custom difficulty badges

### Functional Customization
- Additional scoring metrics
- Custom validation rules
- Game-specific scoring formats
- Custom time periods

## Troubleshooting

### Common Issues
1. **JavaScript Errors**: Template syntax warnings are normal - IDE parses Jinja2 as JS
2. **Database Connection**: Ensure MySQL server is running and credentials are correct
3. **Missing Tables**: Run the database schema script if tables don't exist
4. **Performance**: Use the rankings cache for large datasets

### Debug Mode
Enable debug logging in Flask to see detailed error messages:
```python
app.logger.setLevel(logging.DEBUG)
```

## Future Enhancements

### Planned Features
- Real-time WebSocket updates
- Achievement system integration
- Social sharing capabilities
- Mobile app API
- Advanced analytics dashboard

### Extensibility
The system is designed to be easily extended:
- New game types
- Additional validation rules
- Custom ranking algorithms
- Third-party integrations

## Support

For issues and questions:
1. Check the application logs
2. Verify database connectivity
3. Review validation rules configuration
4. Test API endpoints directly

The leaderboard system provides a solid foundation for competitive gaming features with room for customization and expansion based on specific needs.
