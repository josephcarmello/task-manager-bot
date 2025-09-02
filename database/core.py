# Contains core database connection, initialization for shared tables, and shared utility functions.
import sqlite3
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
DATABASE_PATH = os.getenv("DATABASE_PATH", "task_manager.db")

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DATABASE_PATH, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}", exc_info=True)
        return None

def initialize_database():
    """Initializes the database by creating shared tables (e.g., users)."""
    conn = get_db_connection()
    if not conn:
        logger.critical("Could not establish database connection for core initialization.")
        return

    try:
        cursor = conn.cursor()
        # users table is shared across multiple cogs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY
            )
        """)
        conn.commit()
        logger.info("Core database tables initialized successfully.")
    except sqlite3.Error as e:
        logger.error(f"Error during core database initialization: {e}", exc_info=True)
    finally:
        conn.close()

def _ensure_user_exists(cursor, user_id: int):
    """
    A shared helper function to ensure a user exists in the users table.
    This should be called within a transaction by other DB modules.
    """
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))

def get_total_users() -> int:
    """Returns the total number of unique users in the shared users table."""
    conn = get_db_connection()
    if not conn:
        return 0

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(user_id) FROM users")
        result = cursor.fetchone()
        return result[0] if result else 0
    except sqlite3.Error as e:
        logger.error(f"Error getting total users: {e}", exc_info=True)
        return 0
    finally:
        conn.close()

