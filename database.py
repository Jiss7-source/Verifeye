import sqlite3
from datetime import datetime

# This is the name of the database file that will be created in your project folder.
# SQLite stores everything in a single .db file — no separate server needed.
DB_NAME = "audit_history.db"


def _get_connection():
    """
    A private helper that opens a connection to the database.

    The underscore at the start (_) is a Python convention meaning
    "this is meant for internal use only — don't call this from app.py".

    sqlite3.connect() either opens the existing .db file or creates it
    fresh if it doesn't exist yet. Think of it like opening a filing cabinet.
    """
    return sqlite3.connect(DB_NAME)


def init_db():
    """
    Creates the audits table if it doesn't already exist.

    Call this ONCE when your app starts up (at the top of app.py).
    It's safe to call multiple times — the IF NOT EXISTS part means
    it won't wipe your data if the table already exists.

    The table has these columns:
        id        -> auto-numbered (1, 2, 3...), used as a unique identifier
        filename  -> the name of the uploaded file (e.g. "receipt.pdf")
        verdict   -> the AI's decision (e.g. "APPROVED", "FLAGGED", "REJECTED")
        summary   -> the AI's explanation of its verdict
        flagged   -> 1 if the expense was flagged, 0 if it passed (easy to filter)
        timestamp -> when the audit happened (e.g. "2025-01-15 14:32")
    """
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audits (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                filename  TEXT    NOT NULL,
                verdict   TEXT    NOT NULL,
                summary   TEXT    NOT NULL,
                flagged   INTEGER NOT NULL DEFAULT 0,
                timestamp TEXT    NOT NULL
            )
        """)
        conn.commit()
    finally:
        conn.close()  # Always close, even if something crashes above


def save_audit(filename, verdict, summary):
    """
    Saves one audit result into the database.

    Call this in app.py after Gemini returns its verdict, like:
        save_audit("receipt.pdf", "FLAGGED", "Amount exceeds policy limit.")

    The 'flagged' column is set to 1 automatically if the verdict
    is not APPROVED — this makes filtering easy later.
    """
    flagged = 0 if verdict.upper() == "APPROVED" else 1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audits (filename, verdict, summary, flagged, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (filename, verdict, summary, flagged, timestamp))
        # The ? placeholders prevent SQL injection — a basic security best practice.
        # Never build SQL strings using f-strings or + with user data.
        conn.commit()
    finally:
        conn.close()


def get_all_audits():
    """
    Returns all past audit results, newest first.

    Each row comes back as a tuple like:
        (id, filename, verdict, summary, flagged, timestamp)

    In app.py you can loop through them like:
        for row in get_all_audits():
            print(row[1])  # filename
            print(row[2])  # verdict
    """
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audits ORDER BY id DESC")
        rows = cursor.fetchall()
        return rows
    finally:
        conn.close()


def get_flagged_audits():
    """
    Returns only the audits that were flagged or rejected.

    Useful for a dashboard that shows 'problem expenses' separately
    from approved ones. Good detail to mention in your presentation!
    """
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audits WHERE flagged = 1 ORDER BY id DESC")
        rows = cursor.fetchall()
        return rows
    finally:
        conn.close()


def delete_all_audits():
    """
    Clears all records from the database.

    Useful for a 'Clear History' button in your Streamlit app.
    The table itself stays — only the data inside is deleted.
    """
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM audits")
        conn.commit()
    finally:
        conn.close()
