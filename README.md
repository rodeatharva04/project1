# Pastebin-Lite
A simple service to create and share text pastes with TTL and view limits.

## Local Run
1. pip install -r requirements.txt
2. python manage.py migrate
3. python manage.py runserver

## Persistence
Uses PostgreSQL for production (Vercel) to ensure data survives across requests. SQLite is used for local development.

## Design Decisions
- UUIDs are used for IDs to prevent link guessing.
- `x-test-now-ms` header support is implemented for deterministic testing.
- Database transactions are handled by Django's default model saving logic.