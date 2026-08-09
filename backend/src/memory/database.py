
import sqlite3
from datetime import datetime
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "krishi_mitra.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS farmer_profiles (
            user_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            language_preference TEXT,
            crops_grown TEXT,
            land_size TEXT,
            district TEXT,
            irrigation_type TEXT,
            last_interaction TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def get_farmer(user_id: str):
    conn = get_connection()

    cursor = conn.execute(
        """
        SELECT
            user_id,
            name,
            language_preference,
            crops_grown,
            land_size,
            district,
            irrigation_type,
            last_interaction
        FROM farmer_profiles
        WHERE user_id = ?
        """,
        (user_id,),
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        "user_id": row[0],
        "name": row[1],
        "language_preference": row[2],
        "crops_grown": row[3],
        "land_size": row[4],
        "district": row[5],
        "irrigation_type": row[6],
        "last_interaction": row[7],
    }


def save_farmer(
    user_id: str,
    name: str,
    language_preference: str = "",
    crops_grown: str = "",
    land_size: str = "",
    district: str = "",
    irrigation_type: str = "",
):
    conn = get_connection()

    now = datetime.now().isoformat()

    conn.execute(
        """
        INSERT INTO farmer_profiles (
            user_id,
            name,
            language_preference,
            crops_grown,
            land_size,
            district,
            irrigation_type,
            last_interaction
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)

        ON CONFLICT(user_id)
        DO UPDATE SET
            name = excluded.name,
            language_preference = excluded.language_preference,
            crops_grown = excluded.crops_grown,
            land_size = excluded.land_size,
            district = excluded.district,
            irrigation_type = excluded.irrigation_type,
            last_interaction = excluded.last_interaction
        """,
        (
            user_id,
            name,
            language_preference,
            crops_grown,
            land_size,
            district,
            irrigation_type,
            now,
        ),
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Krishi Mitra database initialized successfully.")
