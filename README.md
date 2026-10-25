# College Event Management CRM

A beginner-friendly full-stack event management project built with Flask, SQLite, HTML, CSS, and vanilla JavaScript.

## Features

- Student portal with event listings and registration form
- Flask API endpoints for events and registration
- SQLite persistence for events, leads, and registrations
- Lead tracking for incomplete registration attempts
- Lead conversion when a matching student completes registration
- Duplicate registration prevention per event and phone number
- Admin login with server-side password hash verification
- Session-protected admin dashboard
- Lead status updates: New, Contacted, Converted
- Dashboard metrics and registration table

## Requirements

- Python 3.10 or newer
- pip

## Run locally

1. Extract the project ZIP and open the `college-event-crm` folder in VS Code.
2. Open the VS Code terminal in that folder.
3. Create and activate a virtual environment (recommended).

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Start the application:

```bash
python app.py
```

6. Open `http://127.0.0.1:5000` in your browser.

The SQLite database is created automatically on first startup.

## Demo admin login

- Username: `admin`
- Password: `admin123`

For a different initial password, set `ADMIN_PASSWORD` before the first run. The initial admin account is created only when no `admin` account exists, so changing the environment variable after the database has already been created will not reset its password. Delete `database.db` to recreate the demo database (this also deletes stored demo data).

For PowerShell, before the first run:

```powershell
$env:ADMIN_PASSWORD = "choose-a-strong-password"
$env:SECRET_KEY = "a-long-random-secret"
python app.py
```

Do not use demo credentials or the development secret in a public deployment.

## Main routes

- `GET /` — student portal
- `GET /login` — admin login
- `POST /logout` — log out
- `GET /admin` — session-protected dashboard
- `GET /api/events` — event list (JSON)
- `POST /api/register` — submit interest or complete registration (JSON)
- `GET /api/dashboard` — CRM dashboard data (admin session required)
- `POST /api/leads/<id>/status` — update a lead status (admin session required)

## How lead conversion works

An incomplete attempt (missing/invalid phone number) is saved as a lead. When a registration is completed, the app first looks for a lead with the same phone and event, then falls back to a matching name and event. Name matching is only a simple demo fallback and is not a reliable identity check for production use.

## Important notes

- The registration flow is a demo: it does not send real email/SMS notifications.
- This is suitable as a learning project, not a production-ready deployment. Before public deployment, add CSRF protection for form-based session actions, rate limiting, stronger input validation, secure production cookie settings, database migration/backup practices, and a proper admin password management flow.
- The development server runs with `debug=True`; do not use it in production.
