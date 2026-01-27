# Pastebin Lite

A simple Pastebin clone built with Django.

## Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

3. **Start Server**
2. **Run Server**
   ```bash
   python manage.py runserver
   ```
   The app will be available at `http://localhost:8000`.

## Running Tests

You can check the deployed application using `curl` or any API client.

**Health Check**
```bash
curl -i http://localhost:8000/api/healthz
```

**Create Paste**
```bash
curl -X POST http://localhost:8000/api/pastes -H "Content-Type: application/json" -d '{"content": "test"}'
```

**Note:** For full TTL verification, ensure `TEST_MODE=1` is set in your environment variables to enable time-travel logic via `x-test-now-ms` header.

## Persistence Layer

**Choice:** SQLite (via Django ORM)
**Reasoning:** SQLite provides file-based persistence that survives individual requests and server restarts, fulfilling the requirement to avoid purely in-memory storage (like global variables). It is lightweight and requires zero configuration for this assessment.

## Deployment (Railway)

1. **Push to GitHub**: Commit all changes and push to your repository.
2. **Create Project on Railway**: Import your repo.
3. **Add Database**: Add a PostgreSQL service.
4. **Variables**:
   - `DJANGO_SECRET_KEY`: (Random string)
   - `DEBUG`: `False`
   - `TEST_MODE`: `0`
   - `DISABLE_COLLECTSTATIC`: `0`

## Design Decisions

- **Framework**: Django was chosen for its robust ORM and security features (CSRF, SQL injection protection).
- **Persistence**: SQLite (local) / PostgreSQL (prod) via `dj-database-url` for seamless switching.
- **Testing**: `verify.py` performs black-box testing against the deployed or local API.
- **Deterministic Time**: Handled via `TEST_MODE` env var and `x-test-now-ms` header to allow reliable TTL testing.