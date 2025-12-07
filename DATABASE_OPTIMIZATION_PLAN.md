# Database Schema Optimization Plan

This document provides a comprehensive analysis of the current database schema and a detailed plan for its optimization. The goal is to improve the system's architecture, performance, and maintainability.

## 1. Table Retention Analysis

Based on the analysis of the application's functionality, the following tables are considered core and must be retained:

- **`users` (4 rows):** Essential for user management, authentication, and storing user profile information.
- **`games` (10 rows) and `game_access` (10 rows):** Core to the gaming functionality, managing available games and user access rights.
- **`audit_logs` (920 rows):** Important for security and compliance, providing a trail of significant user actions.
- **`leaderboard_scores` (assuming `scores`):** Fundamental for tracking user performance and driving the leaderboard system.
- **`streaks`:**  Fundamental for tracking user performance and engagement.
- **`points_transactions` and `user_points`:** Necessary for the points and rewards system, tracking how users earn and spend points.

## 2. Table Removal Recommendations

The following tables are recommended for consolidation or removal:

- **`badges` and `user_badges`:**
  - **Recommendation:** Consolidate these two tables into a single `badges` table. The `user_badges` table can be replaced by a many-to-many relationship table (`user_badges_association`) between `users` and the new `badges` table. This will simplify the schema and reduce redundancy.
  - **Rationale:** A single `badges` table can store all badge definitions, and the association table can track which users have earned which badges.

- **`blog_posts` (1 row):**
  - **Recommendation:** Evaluate the long-term vision for the blog feature. If it's a core feature that will be expanded, it should remain. If it's a minor feature with minimal usage, consider moving the content to a static page or a simpler format (e.g., a JSON file) and removing the table.
  - **Rationale:** A dedicated table for a single blog post might be overkill.

- **`click_events`:**
  - **Recommendation:** Consolidate the data from `click_events` into `audit_logs`.
  - **Rationale:** The `audit_logs` table is already designed to track user actions. Adding click events to this table will centralize all user activity logging and simplify analysis. A new `event_type` column can be added to `audit_logs` to distinguish click events from other audited actions.

- **`otp_verification` (5 rows):**
  - **Recommendation:** For now, keep this table.
  - **Rationale:** While it's possible to handle OTP verification within the `users` table, a separate table provides a cleaner separation of concerns and is easier to manage. The low row count doesn't pose a performance issue.

## 3. Schema Enhancement Proposals

The following new tables are recommended to improve the system's structure:

- **`game_categories`:**
  - **Purpose:** To better organize games and allow users to browse by category.
  - **Proposed Schema:**
    ```sql
    CREATE TABLE game_categories (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        description TEXT
    );
    ```
  - **Relationship:** A many-to-many relationship between `games` and `game_categories` (using a `game_category_association` table).

- **`user_sessions`:**
  - **Purpose:** To track active user sessions, which is crucial for security and real-time monitoring.
  - **Proposed Schema:**
    ```sql
    CREATE TABLE user_sessions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        session_token VARCHAR(255) NOT NULL UNIQUE,
        ip_address VARCHAR(45),
        user_agent VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    ```

- **`notification_preferences`:**
  - **Purpose:** To allow users to customize which notifications they receive.
  - **Proposed Schema:**
    ```sql
    CREATE TABLE notification_preferences (
        user_id INT PRIMARY KEY,
        email_notifications BOOLEAN DEFAULT TRUE,
        sms_notifications BOOLEAN DEFAULT FALSE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    ```

- **`api_keys`:**
  - **Purpose:** To manage access for third-party integrations.
  - **Proposed Schema:**
    ```sql
    CREATE TABLE api_keys (
        id INT AUTO_INCREMENT PRIMARY KEY,
        key_hash VARCHAR(255) NOT NULL UNIQUE,
        user_id INT,
        permissions TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    ```

- **`content_versions`:**
  - **Purpose:** If the blog functionality is kept, this table will provide version control for blog posts.
  - **Proposed Schema:**
    ```sql
    CREATE TABLE content_versions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        content_id INT NOT NULL,
        content_type VARCHAR(50) NOT NULL, -- e.g., 'blog_post'
        version_number INT NOT NULL,
        content TEXT NOT NULL,
        author_id INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL
    );
    ```

## 4. Implementation Guidelines

The migration will be performed in three phases:

### Phase 1: Data Migration and Table Removal
1.  **Backup:** Create a full backup of the database.
2.  **Migrate Data:**
    -   Consolidate `badges` and `user_badges` into a new `badges` table and a `user_badges_association` table.
    -   Migrate `click_events` data to `audit_logs`.
3.  **Remove Deprecated Tables:**
    -   `DROP TABLE user_badges;`
    -   `DROP TABLE click_events;`
    -   (If applicable) `DROP TABLE blog_posts;`

### Phase 2: New Table Implementation
1.  **Create New Tables:**
    -   `game_categories`
    -   `user_sessions`
    -   `notification_preferences`
    -   `api_keys`
    -   (If applicable) `content_versions`
2.  **Establish Relationships:** Create the necessary foreign key constraints to link the new tables with the existing ones.

### Phase 3: Application Code Updates
1.  **Update Models:** Update the application's data models to reflect the schema changes.
2.  **Update Business Logic:** Modify the application's business logic to use the new tables and relationships.
3.  **Update UI:** Update the user interface to expose the new features (e.g., game categories, notification preferences).

## 5. Performance Considerations

-   **`audit_logs` (920 rows):** This table has the potential to grow very large.
    -   **Recommendation:** Implement a partitioning strategy based on the `created_at` column (e.g., monthly partitions). This will improve query performance and make it easier to manage old data.
-   **`leaderboard_scores`:** This table is also expected to grow large.
    -   **Recommendation:** Create indexes on `(game_id, score_value)` and `(user_id, game_id)` to speed up leaderboard queries.
-   **Indexing:** Review all high-usage tables and ensure that they have appropriate indexes on columns that are frequently used in `WHERE` clauses and `JOIN` conditions.

## Final Recommendation

### Proposed Schema Diagram (Text-based)

```
[users]
  - id (PK)
  - username
  - ...

[games]
  - id (PK)
  - name
  - ...

[game_access]
  - user_id (FK to users.id)
  - game_id (FK to games.id)

[audit_logs]
  - id (PK)
  - user_id (FK to users.id)
  - action
  - ...

[leaderboard_scores]
  - id (PK)
  - user_id (FK to users.id)
  - game_id (FK to games.id)
  - score_value
  - ...

[streaks]
 - id (PK)
 - user_id (FK to users.id)
 - game_id (FK to games.id)
 - streak_count
 - ...

[user_points]
 - user_id (PK, FK to users.id)
 - points
 - ...

[points_transactions]
 - id (PK)
 - user_id (FK to users.id)
 - points
 - reason
 - ...

[badges]
  - id (PK)
  - name
  - ...

[user_badges_association]
  - user_id (FK to users.id)
  - badge_id (FK to badges.id)

[game_categories]
  - id (PK)
  - name
  - ...

[game_category_association]
    - game_id (FK to games.id)
    - category_id (FK to game_categories.id)

[user_sessions]
  - id (PK)
  - user_id (FK to users.id)
  - ...

[notification_preferences]
    - user_id (PK, FK to users.id)
    - ...

[api_keys]
    - id (PK)
    - user_id (FK to users.id)
    - ...

[content_versions]
    - id (PK)
    - ...
```

### SQL Scripts

The specific SQL scripts for the schema changes will be provided in a separate file.

### Data Migration Procedures

Detailed data migration scripts (e.g., Python scripts using an ORM) will be provided to ensure a smooth transition.

### Impact Analysis

-   **Queries and Reports:** All queries and reports that use the deprecated tables will need to be updated.
-   **Application Code:** The application code will need to be updated to use the new schema. This will be the most significant part of the migration.
-   **Performance:** The proposed changes are expected to improve performance by optimizing the schema and adding appropriate indexes.

### Testing Requirements

-   **Unit Tests:** All new and modified code will be covered by unit tests.
-   **Integration Tests:** Integration tests will be created to verify that the different components of the application work together correctly.
-   **End-to-End Tests:** End-to-end tests will be performed to simulate real user scenarios and ensure that the application is working as expected.
-   **Performance Tests:** Performance tests will be conducted to measure the impact of the schema changes on the application's performance.
-   **Data Validation:** After the migration, the data will be validated to ensure that no data was lost or corrupted during the process.
