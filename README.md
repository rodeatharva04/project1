# Pastebin-Lite

## Local Run
1. `pip install -r requirements.txt`
2. `python manage.py migrate`
3. `python manage.py runserver`

## Persistence Layer
I used **PostgreSQL** as the persistence layer. This ensures that data survives across serverless restarts and satisfies the requirement for a layer that survives across requests.

## Design Decisions
- **UUIDs**: Used for Paste IDs to prevent link guessing and enumeration.
- **Select For Update**: Implemented database-level row locking within atomic transactions to ensure `current_views` is updated accurately under concurrent load.
- **Time Determinism**: Built a helper to respect `x-test-now-ms` when `TEST_MODE=1` is set, enabling deterministic bot testing.
- **Safe Rendering**: All content is rendered inside `<pre>` tags and automatically escaped by Django's template engine to prevent script execution.
