# Pastebin-Lite

A lightweight service to create and share text pastes with TTL and view limits.

## Local Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Run migrations: `python manage.py migrate`
3. Start server: `python manage.py runserver`

## Persistence Layer
I used **PostgreSQL** as the persistence layer. This ensures that paste data survives across requests and server restarts in the serverless Railway environment.

## Design Decisions
- **UUIDs**: Used for Paste IDs to prevent link guessing and enumeration.
- **Atomic Transactions**: Used `select_for_update()` to handle concurrent view-count increments safely.
- **Deterministic Expiry**: Implemented custom logic to respect the `x-test-now-ms` header when `TEST_MODE` is enabled, allowing automated bots to test time-based expiry accurately.
- **Security**: Content is rendered within `<pre>` tags and escaped by Django's template engine to prevent XSS.
