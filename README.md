# Pastebin Lite

A secure, scalable pastebin service built with Django. This application allows users to create text pastes with optional expiration (TTL) and view limits.

## Table of Contents
- [Features](#features)
- [Local Development](#local-development)
  - [Prerequisites](#prerequisites)
  - [Setup Instructions](#setup-instructions)
- [Persistence Layer](#persistence-layer)
- [Design Decisions](#design-decisions)
- [Deployment](#deployment)
- [Testing](#testing)

## Deployed Application
**URL**: [https://project1-production-b60c.up.railway.app/](https://project1-production-b60c.up.railway.app/)


## Features
- **Create Pastes**: Store arbitrary text.
- **Expiration Controls**:
  - Time-to-Live (TTL): Paste expires after a set duration.
  - View Limits: Paste expires after a set number of views.
- **Deterministic Testing**: Support for time-travel testing via `x-test-now-ms` headers.
- **Race Condition Handling**: Robust view counting using atomic database transactions.

## Local Development

### Prerequisites
- Python 3.8+
- pip

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. **Create and Activate a Virtual Environment**
   It is recommended to run this project in an isolated virtual environment.
   
   *Windows:*
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate
   ```
   
   *macOS/Linux:*
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Database Migrations**
   Initialize the local SQLite database.
   ```bash
   python manage.py migrate
   ```

5. **Start the Development Server**
   ```bash
   python manage.py runserver
   ```
   The application will be available at [http://localhost:8000](http://localhost:8000).

## Persistence Layer

This application uses a flexible persistence layer configured via `dj-database-url`:

- **Development**: Uses **SQLite** (`db.sqlite3`) by default. This ensures a zero-setup local environment where the database is a simple file on disk, surviving across server restarts.
- **Production**: Designed to use **PostgreSQL**. The application checks the `DATABASE_URL` environment variable to connect to a production-grade database (e.g., on Railway, Heroku, or Vercel).

This approach balances developer experience (ease of setup) with production reliability.

## Design Decisions

### 1. Framework Choice: Django
Django was selected for its:
- **Security**: Built-in protection against SQL injection, XSS, and CSRF.
- **ORM**: Powerful abstraction for database interactions allowing seamless switching between SQLite and Postgres.
- **Speed**: Rapid development of standard CRUD APIs.

### 2. Concurrency & Robustness
To strictly enforce "Max Views" limits under load, the application uses **database-level locking**:
- `select_for_update()` is used within an `atomic` transaction when fetching a paste.
- This prevents race conditions where multiple concurrent requests could read a paste as "available" simultaneously before the view count is incremented.

### 3. Deterministic Time for Testing
To ensure the automated grader can accurately test time-based expiry (TTL):
- The application checks for a `TEST_MODE=1` environment variable.
- If enabled, the `x-test-now-ms` header is used to determine "current time" for expiry logic.
- If the header is missing or `TEST_MODE` is disabled, the system defaults to the server's real time.

### 4. API & Security
- **Endpoints**: RESTful JSON APIs for creation and retrieval.
- **HTML View**: The content is rendered inside a `<pre>` tag and explicitly escaped to prevent Stored XSS attacks (ensuring safety when viewing untrusted input).

## Deployment

The project is configured for cloud deployment (e.g., Railway) using a standard `Procfile`.

### Environment Variables
- `DEBUG`: Set to `False` in production.
- `SECRET_KEY`: A long, random string.
- `DATABASE_URL`: Connection string for PostgreSQL.
- `TEST_MODE`: Set to `0` for production, `1` for testing environments.
- `DISABLE_COLLECTSTATIC`: Set to `0` (or `1` if handling statics differently).

## Testing

You can manually verify the API using `curl`.

**Health Check:**
```bash
curl http://localhost:8000/api/healthz
```

**Create a Paste:**
```bash
curl -X POST http://localhost:8000/api/pastes \
     -H "Content-Type: application/json" \
     -d '{"content": "Hello World", "max_views": 5}'
```