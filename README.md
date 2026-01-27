# Pastebin-Lite
## Setup
1. pip install -r requirements.txt
2. python manage.py migrate
3. python manage.py runserver
## Persistence
PostgreSQL via Railway.
## Decisions
- UUIDs for security.
- Atomic transactions for concurrency.
- x-test-now-ms for bot testing.
