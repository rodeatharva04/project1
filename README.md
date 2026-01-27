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
   ```bash
   python manage.py runserver
   ```
   
   The app will be available at http://localhost:8000.

## Running Tests

I have included a script `test_app.py` to verify functionality.

**Basic Verification:**
```bash
python test_app.py
```

**Full Verification (including View Limits & TTL):**
You must run the server with `TEST_MODE=1` to allow time-travel testing.

1. Stop any running server.
2. Start server in test mode:
   *PowerShell:*
   ```powershell
   $env:TEST_MODE='1'; python manage.py runserver
   ```
   *CMD:*
   ```cmd
   set TEST_MODE=1 && python manage.py runserver
   ```
3. Run the test script in another terminal:
   ```bash
   python test_app.py
   ```

## Persistence Layer

This project utilizes **PostgreSQL** when deployed on Railway (via `dj-database-url`) and **SQLite** for local development.

## Deployment (Railway)

1. **Push to GitHub**: Commit all changes and push to your repository.
2. **Create Project on Railway**: Import your repo.
3. **Add Database**: Add a PostgreSQL service in Railway.
4. **Variables**: Set the following environment variables in your Railway Project Settings:
   - `DJANGO_SECRET_KEY`: (Generate a random string)
   - `DEBUG`: `False`
   - `TEST_MODE`: `0`
   - `DISABLE_COLLECTSTATIC`: `0` (Optional, let Railway run collectstatic)
- **Security**: Secret keys and debug modes are controlled via environment variables. `TEST_MODE` allows deterministic time testing without exposing it to production by default.
- **Testing**: The API supports `x-test-now-ms` header when `TEST_MODE=1` to simulate time travel for expiry verification as per requirements.