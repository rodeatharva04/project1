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

To verify functionality, including TTL expiry which uses time-travel:

1. Start the server in TEST_MODE:
   *PowerShell:*
   ```powershell
   $env:TEST_MODE='1'; python manage.py runserver
   ```
   *CMD:*
   ```cmd
   set TEST_MODE=1 && python manage.py runserver
   ```

2. Run the verification script:
   ```bash
   python verify.py
   ```

## Persistence Layer

This project utilizes **PostgreSQL** when deployed on Railway (via `dj-database-url`) and **SQLite** for local development.

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