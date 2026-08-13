
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path


# ============================================================
# DATABASE
# ============================================================

# Analytics database is separate from the farmer memory database.
DB_PATH = Path(__file__).resolve().parents[2] / "call_analytics.db"


def get_connection():
    """Create a connection to the call analytics database."""
    return sqlite3.connect(DB_PATH)


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_analytics_db():
    """Create the calls table if it does not already exist."""

    with get_connection() as conn:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_id TEXT UNIQUE NOT NULL,
                channel TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                outcome TEXT,
                success_reason TEXT
            )
            """
        )

        conn.commit()


# ============================================================
# START CALL
# ============================================================

def start_call(channel: str) -> str:
    """
    Record the beginning of a call.

    channel should be:
    - browser
    - sip
    """

    call_id = str(uuid.uuid4())

    started_at = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as conn:

        conn.execute(
            """
            INSERT INTO calls (
                call_id,
                channel,
                started_at,
                outcome
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                call_id,
                channel,
                started_at,
                "IN_PROGRESS",
            ),
        )

        conn.commit()

    return call_id


# ============================================================
# END CALL
# ============================================================

def end_call(
    call_id: str,
    outcome: str,
    success_reason: str = "",
):
    """
    Record the end of a call.

    outcome should be:
    - SUCCESS
    - FAILED
    """

    ended_at = datetime.now(
        timezone.utc
    ).isoformat()

    with get_connection() as conn:

        conn.execute(
            """
            UPDATE calls
            SET
                ended_at = ?,
                outcome = ?,
                success_reason = ?
            WHERE call_id = ?
            """,
            (
                ended_at,
                outcome,
                success_reason,
                call_id,
            ),
        )

        conn.commit()


# ============================================================
# OVERALL CALL METRICS
# ============================================================

def get_call_metrics():
    """
    Return the overall Day 8 required metrics.

    Returns:
        total_calls
        successful_calls
        failed_calls
    """

    with get_connection() as conn:

        total = conn.execute(
            """
            SELECT COUNT(*)
            FROM calls
            WHERE outcome IN ('SUCCESS', 'FAILED')
            """
        ).fetchone()[0]

        successful = conn.execute(
            """
            SELECT COUNT(*)
            FROM calls
            WHERE outcome = 'SUCCESS'
            """
        ).fetchone()[0]

        failed = conn.execute(
            """
            SELECT COUNT(*)
            FROM calls
            WHERE outcome = 'FAILED'
            """
        ).fetchone()[0]

    return {
        "total_calls": total,
        "successful_calls": successful,
        "failed_calls": failed,
    }


# ============================================================
# CHANNEL-WISE CALL METRICS
# ============================================================

def get_channel_metrics():
    """
    Return call metrics separated by channel.

    Supported channels:
    - browser
    - sip

    Only completed calls are included in the
    total/success/failed counts.

    IN_PROGRESS calls are intentionally excluded.
    """

    metrics = {
        "browser": {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
        },
        "sip": {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
        },
    }

    with get_connection() as conn:

        rows = conn.execute(
            """
            SELECT
                channel,
                COUNT(*) AS total_calls,
                SUM(
                    CASE
                        WHEN outcome = 'SUCCESS'
                        THEN 1
                        ELSE 0
                    END
                ) AS successful_calls,
                SUM(
                    CASE
                        WHEN outcome = 'FAILED'
                        THEN 1
                        ELSE 0
                    END
                ) AS failed_calls
            FROM calls
            WHERE
                channel IN ('browser', 'sip')
                AND outcome IN ('SUCCESS', 'FAILED')
            GROUP BY channel
            """
        ).fetchall()

    for row in rows:

        channel = str(
            row[0]
        ).lower()

        if channel not in metrics:
            continue

        metrics[channel] = {
            "total_calls": int(
                row[1] or 0
            ),
            "successful_calls": int(
                row[2] or 0
            ),
            "failed_calls": int(
                row[3] or 0
            ),
        }

    return metrics


# ============================================================
# RECENT CALLS
# ============================================================

def get_recent_calls(limit: int = 20):
    """
    Return recent completed calls for the dashboard.

    Returns:
        started_at
        channel
        outcome
    """

    with get_connection() as conn:

        rows = conn.execute(
            """
            SELECT
                started_at,
                channel,
                outcome
            FROM calls
            WHERE outcome IN ('SUCCESS', 'FAILED')
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return rows


# ============================================================
# INITIALIZE DATABASE
# ============================================================

init_analytics_db()
