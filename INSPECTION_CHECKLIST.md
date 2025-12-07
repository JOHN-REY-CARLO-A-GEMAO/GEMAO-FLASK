# Project Inspection Checklist

This document outlines a comprehensive checklist for examining the GEMAO-FLASK application. The inspection covers code functionality, system performance, security vulnerabilities, user interface elements, data integrity, and integration points.

## 1. Authentication

### 1.1. Code Functionality
- **[ ] User Registration:**
  - **Expected State:** New users can register with a unique username and email. Passwords are securely hashed before being stored.
  - **Validation:** Create a new user account through the registration form. Check the `users` table in the database to ensure the new user is added and the password field contains a hashed value.
- **[ ] User Login:**
  - **Expected State:** Registered users can log in with their credentials. A session is created for the user.
  - **Validation:** Log in with a test user account. Verify that the user is redirected to the correct dashboard and that a session cookie is present in the browser.
- **[ ] User Logout:**
  - **Expected State:** Logged-in users can log out. The session is destroyed.
  - **Validation:** Log out from an active session. Verify that the user is redirected to the homepage and that the session cookie is removed.
- **[ ] Password Reset:**
  - **Expected State:** Users can request a password reset. An email with a unique token is sent to the user's registered email address.
  - **Validation:** Use the "Forgot Password" feature. Check the email inbox for the password reset email. Verify that the link in the email leads to a password reset form.
- **[ ] Role-Based Access Control (RBAC):**
  - **Expected State:** The application correctly enforces access control based on user roles (Admin vs. User).
  - **Validation:** Attempt to access admin-only pages (e.g., `/admin/dashboard`) as a regular user. Verify that access is denied.

### 1.2. Security
- **[ ] Password Hashing:**
  - **Expected State:** User passwords are not stored in plaintext. They are hashed using a strong, one-way hashing algorithm (e.g., bcrypt, Argon2).
  - **Validation:** Inspect the `users` table to confirm that the `password` column contains hashed values.
- **[ ] CSRF Protection:**
  - **Expected State:** All forms that perform state-changing actions are protected against Cross-Site Request Forgery (CSRF) attacks.
  - **Validation:** Inspect all forms in the application to ensure they contain a hidden CSRF token. Use a tool like Burp Suite to attempt to submit a form without a CSRF token.
- **[ ] Session Security:**
  - **Expected State:** Session cookies are configured with the `HttpOnly`, `Secure`, and `SameSite` attributes to prevent session hijacking.
  - **Validation:** Use browser developer tools to inspect the session cookie and verify that the security attributes are set correctly.

## 2. Admin Dashboard

### 2.1. Code Functionality
- **[ ] User Management:**
  - **Expected State:** Admins can view, add, edit, and delete users.
  - **Validation:** Perform CRUD (Create, Read, Update, Delete) operations on users through the admin dashboard. Verify that the changes are reflected in the database.
- **[ ] Game Management:**
  - **Expected State:** Admins can manage game access for users.
  - **Validation:** Grant and revoke game access for a test user. Log in as the test user and verify that they can only access the allowed games.

## 3. Leaderboard System

### 3.1. Code Functionality
- **[ ] Score Submission:**
  - **Expected State:** Users can submit scores for games. The scores are correctly stored in the `leaderboard_scores` table.
  - **Validation:** Play a game and submit a score. Verify that a new entry is created in the `leaderboard_scores` table with the correct user ID, game ID, and score.
- **[ ] Score Validation:**
  - **Expected State:** The system validates scores to prevent cheating. Invalid scores are rejected.
  - **Validation:** Attempt to submit a score that violates the validation rules (e.g., a score that is too high). Verify that the score is rejected.
- **[ ] Average Score Calculation:**
  - **Expected State:** The `average_score` in the `user_personal_bests` table is correctly calculated and updated after each new score submission.
  - **Validation:** Submit multiple scores for a user and game. Verify that the `average_score` in the `user_personal_bests` table is updated correctly after each submission.

### 3.2. Data Integrity
- **[ ] Foreign Key Constraints:**
  - **Expected State:** The foreign key constraints in the leaderboard tables are enforced.
  - **Validation:** Attempt to insert a score for a non-existent user or game. Verify that the database rejects the insertion.

## 4. Database

### 4.1. Data Integrity
- **[ ] Data Consistency:**
  - **Expected State:** The data in the database is consistent and accurate.
  - **Validation:** Manually review the data in the database to check for any inconsistencies or anomalies.
- **[ ] Backups:**
  - **Expected State:** The database is regularly backed up to prevent data loss.
  - **Validation:** Review the backup and recovery procedures to ensure they are in place and working correctly.

## Tools, Logs, and Metrics

- **Browser Developer Tools:** For inspecting network requests, session cookies, and frontend code.
- **Database Client (e.g., DBeaver, MySQL Workbench):** For directly inspecting the database.
- **Application Logs (`logs/app.log`):** For reviewing application errors and debug information.
- **Security Scanner (e.g., Burp Suite, OWASP ZAP):** For identifying security vulnerabilities.
- **Code Editor (e.g., VS Code):** For inspecting the source code.
