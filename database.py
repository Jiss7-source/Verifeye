import sqlite3
from datetime import datetime

# This is the name of the database file that will be created in your project folder.
# SQLite stores everything in a single .db file — no separate server needed.
DB_NAME = "audit_history.db"


def _get_connection():
    """
    A private helper that opens a connection to the database.
    """
    return sqlite3.connect(DB_NAME)


def init_db():
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
        
        # Migration: Add new columns for Feature 1 and Feature 3 if they don't exist
        try:
            cursor.execute("ALTER TABLE audits ADD COLUMN business_purpose TEXT")
            cursor.execute("ALTER TABLE audits ADD COLUMN claimed_date TEXT")
            cursor.execute("ALTER TABLE audits ADD COLUMN human_comment TEXT")
            cursor.execute("ALTER TABLE audits ADD COLUMN human_verdict TEXT")
        except sqlite3.OperationalError:
            pass  # Columns already exist

        conn.commit()
    finally:
        conn.close()  # Always close, even if something crashes above


def save_audit(filename, business_purpose, claimed_date, verdict, summary):
    """
    Saves one audit result into the database, now tracking business purpose and date.
    """
    flagged = 0 if verdict.upper() == "APPROVED" else 1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn = _get_connection()
    try:
        cursor = conn.cursor()
        
        # Check if new columns exist by trying to insert into them
        # if it fails because it's an old DB and migration didn't run, we fallback.
        cursor.execute("""
            INSERT INTO audits (filename, business_purpose, claimed_date, verdict, summary, flagged, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (filename, business_purpose, claimed_date, verdict, summary, flagged, timestamp))
        
        conn.commit()
    finally:
        conn.close()

def update_audit_override(audit_id, human_comment, human_verdict):
    """
    Allows a human to override the AI verdict and add a comment.
    """
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        flagged = 0 if human_verdict.upper() == "APPROVED" else 1
        cursor.execute("""
            UPDATE audits 
            SET human_comment = ?, human_verdict = ?, flagged = ? 
            WHERE id = ?
        """, (human_comment, human_verdict, flagged, audit_id))
        conn.commit()
    finally:
        conn.close()

def get_all_audits():
    """
    Returns all past audit results, newest first.
    Returns: list of dicts.
    """
    conn = _get_connection()
    conn.row_factory = sqlite3.Row  # Access columns by name
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audits ORDER BY id DESC")
        rows = [dict(r) for r in cursor.fetchall()]
        return rows
    finally:
        conn.close()


def get_flagged_audits():
    """
    Returns only the audits that were flagged or rejected.
    """
    conn = _get_connection()
    conn.row_factory = sqlite3.Row
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audits WHERE flagged = 1 ORDER BY id DESC")
        rows = [dict(r) for r in cursor.fetchall()]
        return rows
    finally:
        conn.close()


def delete_all_audits():
    """
    Clears all records from the database.
    """
    conn = _get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM audits")
        conn.commit()
    finally:
        conn.close()
