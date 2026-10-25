import os
import sqlite3
from functools import wraps
from datetime import datetime
from flask import Flask, jsonify, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-development-secret")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            event_date TEXT NOT NULL,
            venue TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            email TEXT,
            event_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'New',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(event_id) REFERENCES events(id)
        );
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            event_id INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(phone, event_id),
            FOREIGN KEY(event_id) REFERENCES events(id)
        );
        """)
        admin = db.execute("SELECT id FROM admins WHERE username = ?", ("admin",)).fetchone()
        if not admin:
            db.execute(
                "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
                ("admin", generate_password_hash(os.environ.get("ADMIN_PASSWORD", "admin123")))
            )
        count = db.execute("SELECT COUNT(*) AS n FROM events").fetchone()["n"]
        if count == 0:
            db.executemany(
                "INSERT INTO events (title, description, event_date, venue) VALUES (?, ?, ?, ?)",
                [
                    ("CodeOMania", "A day of coding, innovation, and technical competitions.", "2026-11-23", "Seminar Hall"),
                    ("Cultural Night", "Music, dance, performances, and student showcases.", "2026-11-22", "Auditorium"),
                    ("Hackathon Sprint", "Build a prototype with a team and present your solution.", "2026-11-25", "Cafeteria"),
            ]
            )


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required"}), 401
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def index():
    with get_db() as db:
        events = db.execute("SELECT * FROM events ORDER BY event_date").fetchall()
    return render_template("index.html", events=events)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with get_db() as db:
            admin = db.execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
        if admin and check_password_hash(admin["password_hash"], password):
            session.clear()
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/admin")
@admin_required
def dashboard():
    return render_template("admin.html", username=session.get("admin_username", "Admin"))


@app.get("/api/events")
def api_events():
    with get_db() as db:
        rows = db.execute("SELECT * FROM events ORDER BY event_date").fetchall()
    return jsonify([dict(row) for row in rows])


@app.post("/api/register")
def api_register():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    phone = "".join(ch for ch in str(data.get("phone", "")) if ch.isdigit())
    email = str(data.get("email", "")).strip().lower()
    event_id = data.get("event_id")

    if not name or not event_id:
        return jsonify({"error": "Please provide your name and choose an event."}), 400
    try:
        event_id = int(event_id)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid event selected."}), 400

    with get_db() as db:
        event = db.execute("SELECT id FROM events WHERE id = ?", (event_id,)).fetchone()
        if not event:
            return jsonify({"error": "This event does not exist."}), 404

        now = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        # A missing/invalid phone is tracked as a lead rather than a completed registration.
        if len(phone) < 10:
            existing = db.execute(
                "SELECT id FROM leads WHERE lower(name) = lower(?) AND event_id = ? AND status != 'Converted'",
                (name, event_id)
            ).fetchone()
            if existing:
                db.execute(
                    "UPDATE leads SET phone = ?, email = ?, updated_at = ? WHERE id = ?",
                    (phone or None, email or None, now, existing["id"])
                )
            else:
                db.execute(
                    "INSERT INTO leads (name, phone, email, event_id, status, created_at, updated_at) VALUES (?, ?, ?, ?, 'New', ?, ?)",
                    (name, phone or None, email or None, event_id, now, now)
                )
            return jsonify({"message": "Your interest has been saved. Add a valid phone number to complete registration.", "type": "lead"}), 201

        if not email or "@" not in email:
            return jsonify({"error": "Please enter a valid email address to complete registration."}), 400

        existing_registration = db.execute(
            "SELECT id FROM registrations WHERE phone = ? AND event_id = ?",
            (phone, event_id)
        ).fetchone()
        if existing_registration:
            return jsonify({"error": "This phone number is already registered for this event."}), 409

        db.execute(
            "INSERT INTO registrations (name, phone, email, event_id, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, phone, email, event_id, now)
        )
        lead = db.execute(
            "SELECT id FROM leads WHERE phone = ? AND event_id = ? ORDER BY id DESC LIMIT 1",
            (phone, event_id)
        ).fetchone()
        if not lead:
            lead = db.execute(
                "SELECT id FROM leads WHERE lower(name) = lower(?) AND event_id = ? ORDER BY id DESC LIMIT 1",
                (name, event_id)
            ).fetchone()
        if lead:
            db.execute(
                "UPDATE leads SET name = ?, phone = ?, email = ?, status = 'Converted', updated_at = ? WHERE id = ?",
                (name, phone, email, now, lead["id"])
            )
        else:
            db.execute(
                "INSERT INTO leads (name, phone, email, event_id, status, created_at, updated_at) VALUES (?, ?, ?, ?, 'Converted', ?, ?)",
                (name, phone, email, event_id, now, now)
            )

    return jsonify({"message": "Registration completed successfully!", "type": "registration"}), 201


@app.get("/api/dashboard")
@admin_required
def api_dashboard():
    with get_db() as db:
        counts = {
            "events": db.execute("SELECT COUNT(*) n FROM events").fetchone()["n"],
            "leads": db.execute("SELECT COUNT(*) n FROM leads").fetchone()["n"],
            "registrations": db.execute("SELECT COUNT(*) n FROM registrations").fetchone()["n"],
            "converted": db.execute("SELECT COUNT(*) n FROM leads WHERE status = 'Converted'").fetchone()["n"],
        }
        leads = db.execute("""
            SELECT leads.id, leads.name, leads.phone, leads.email, leads.status,
                   leads.created_at, events.title AS event_title
            FROM leads JOIN events ON events.id = leads.event_id
            ORDER BY leads.updated_at DESC, leads.id DESC
        """).fetchall()
        registrations = db.execute("""
            SELECT registrations.id, registrations.name, registrations.phone,
                   registrations.email, registrations.created_at, events.title AS event_title
            FROM registrations JOIN events ON events.id = registrations.event_id
            ORDER BY registrations.id DESC
        """).fetchall()
    counts["conversion_rate"] = round((counts["converted"] / counts["leads"] * 100), 1) if counts["leads"] else 0
    return jsonify({"counts": counts, "leads": [dict(x) for x in leads], "registrations": [dict(x) for x in registrations]})


@app.post("/api/leads/<int:lead_id>/status")
@admin_required
def api_update_lead(lead_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if status not in {"New", "Contacted", "Converted"}:
        return jsonify({"error": "Invalid lead status."}), 400
    with get_db() as db:
        result = db.execute(
            "UPDATE leads SET status = ?, updated_at = ? WHERE id = ?",
            (status, datetime.utcnow().isoformat(timespec="seconds") + "Z", lead_id)
        )
        if result.rowcount == 0:
            return jsonify({"error": "Lead not found."}), 404
    return jsonify({"message": "Lead status updated."})


@app.errorhandler(500)
def server_error(_error):
    return jsonify({"error": "An unexpected server error occurred."}), 500


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
