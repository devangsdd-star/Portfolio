import os
import re
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, render_template, request

BASE_DIR = Path(__file__).resolve().parent
DATABASE = Path(os.environ.get("DATABASE_PATH", BASE_DIR / "portfolio.db"))

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024  # Keep contact submissions small.

# Lightweight in-process rate limit. For a larger production app, use Redis.
recent_submissions = {}
RATE_LIMIT_SECONDS = 30


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    DATABASE.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS site_stats (
                key TEXT PRIMARY KEY,
                value INTEGER NOT NULL DEFAULT 0
            )
        """)
        connection.execute(
            "INSERT OR IGNORE INTO site_stats (key, value) VALUES ('visitors', 0)"
        )


def clean_text(value, max_length):
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().split())[:max_length]


@app.get("/")
def home():
    init_db()
    with get_db() as connection:
        connection.execute(
            "UPDATE site_stats SET value = value + 1 WHERE key = 'visitors'"
        )
        visitors = connection.execute(
            "SELECT value FROM site_stats WHERE key = 'visitors'"
        ).fetchone()["value"]
    return render_template("index.html", visitor_count=visitors)


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "portfolio-api"})


@app.post("/api/contact")
def contact():
    init_db()
    data = request.get_json(silent=True) or request.form

    # Honeypot field: real visitors should leave this empty.
    if clean_text(data.get("company", ""), 100):
        return jsonify({"ok": True, "message": "Thanks! Your message has been received."}), 200

    name = clean_text(data.get("name", ""), 80)
    email = clean_text(data.get("email", ""), 120).lower()
    subject = clean_text(data.get("subject", ""), 120) or "Portfolio enquiry"
    message = str(data.get("message", "")).strip()

    errors = {}
    if len(name) < 2:
        errors["name"] = "Please enter your name."
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        errors["email"] = "Please enter a valid email address."
    if len(message) < 10:
        errors["message"] = "Please write at least 10 characters."
    if len(message) > 3000:
        errors["message"] = "Please keep your message under 3000 characters."

    if errors:
        return jsonify({"ok": False, "errors": errors}), 400

    # Avoid repeated rapid submissions from the same client address.
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown").split(",")[0].strip()
    now = time.time()
    previous = recent_submissions.get(client_ip, 0)
    if now - previous < RATE_LIMIT_SECONDS:
        wait = max(1, int(RATE_LIMIT_SECONDS - (now - previous)))
        return jsonify({
            "ok": False,
            "message": f"Please wait {wait} seconds before sending another message."
        }), 429

    with get_db() as connection:
        connection.execute(
            """INSERT INTO messages (name, email, subject, message, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                name,
                email,
                subject,
                message,
                datetime.now(timezone.utc).isoformat(timespec="seconds"),
            ),
        )

    recent_submissions[client_ip] = now
    return jsonify({
        "ok": True,
        "message": "Message sent successfully. Thanks for reaching out!"
    }), 201


if __name__ == "__main__":
    init_db()
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
