"""Human help / escalation tool for Krishi Mitra Day 7."""

import sqlite3
import uuid
from datetime import datetime
from pathlib import Path


# Same database used by database.py
DB_PATH = (
    Path(__file__).resolve().parents[2]
    / "krishi_mitra.db"
)


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_escalation_db():
    """Create the human-help request table."""

    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS escalation_requests (
            reference_id TEXT PRIMARY KEY,
            user_id TEXT,
            farmer_name TEXT,
            district TEXT,
            crop TEXT,
            reason TEXT,
            what_happened TEXT,
            agent_checked TEXT,
            urgency TEXT,
            language TEXT,
            preferred_follow_up TEXT,
            status TEXT,
            created_at TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def create_escalation(
    user_id: str,
    farmer_name: str,
    district: str,
    crop: str,
    reason: str,
    what_happened: str,
    agent_checked: str,
    urgency: str,
    language: str,
    preferred_follow_up: str,
) -> dict:
    """
    Create a human-help request.

    Only call this after the farmer explicitly gives
    permission to share the information.
    """

    init_escalation_db()

    reference_id = (
        "KM-"
        + uuid.uuid4().hex[:8].upper()
    )

    created_at = datetime.now().isoformat()

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO escalation_requests (
            reference_id,
            user_id,
            farmer_name,
            district,
            crop,
            reason,
            what_happened,
            agent_checked,
            urgency,
            language,
            preferred_follow_up,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            reference_id,
            user_id,
            farmer_name,
            district,
            crop,
            reason,
            what_happened,
            agent_checked,
            urgency,
            language,
            preferred_follow_up,
            "OPEN",
            created_at,
        ),
    )

    conn.commit()
    conn.close()

    return {
        "success": True,
        "reference_id": reference_id,
        "status": "OPEN",
    }


def get_open_escalations():
    """Get all unresolved human-help requests."""

    init_escalation_db()

    conn = get_connection()

    cursor = conn.execute(
        """
        SELECT
            reference_id,
            farmer_name,
            district,
            crop,
            reason,
            what_happened,
            agent_checked,
            urgency,
            language,
            preferred_follow_up,
            status,
            created_at
        FROM escalation_requests
        WHERE status != 'RESOLVED'
        ORDER BY created_at DESC
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return rows
