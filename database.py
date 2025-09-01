import sqlite3
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_PATH = os.getenv("DATABASE_PATH", "task_manager.db")

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}", exc_info=True)
        return None

def initialize_database():
    """
    Initializes the database by creating necessary tables if they don't exist.
    """
    conn = get_db_connection()
    if not conn:
        logger.critical("Could not establish database connection for initialization.")
        return

    try:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS balances (
                user_id INTEGER,
                currency TEXT,
                amount INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, currency),
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_usage (
                command_name TEXT PRIMARY KEY,
                usage_count INTEGER DEFAULT 0
            )
        """)

        conn.commit()
        logger.info("Database initialized successfully. Tables are ready.")
    except sqlite3.Error as e:
        logger.error(f"Error during database initialization: {e}", exc_info=True)
    finally:
        conn.close()

def _ensure_user_exists(cursor, user_id: int):
    """
    A helper function to ensure a user exists in the users table.
    This should be called within a transaction.
    """
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))

def get_balance(user_id: int, currency: str) -> int:
    """
    Retrieves the balance of a specific currency for a user.
    Creates the user and their balance entry if they don't exist.
    """
    conn = get_db_connection()
    balance = 0
    if not conn:
        return balance

    try:
        cursor = conn.cursor()
        _ensure_user_exists(cursor, user_id)

        cursor.execute(
            "SELECT amount FROM balances WHERE user_id = ? AND currency = ?",
            (user_id, currency.lower())
        )
        result = cursor.fetchone()

        if result:
            balance = result['amount']
        else:
            cursor.execute(
                "INSERT INTO balances (user_id, currency, amount) VALUES (?, ?, 0)",
                (user_id, currency.lower())
            )

        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error getting balance for user {user_id}: {e}", exc_info=True)
        conn.rollback()
    finally:
        conn.close()

    return balance

def update_balance(user_id: int, currency: str, amount_change: int):
    """
    Updates a user's balance by a certain amount (can be positive or negative).
    """
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        _ensure_user_exists(cursor, user_id)

        currency_lower = currency.lower()

        cursor.execute(
            "INSERT OR IGNORE INTO balances (user_id, currency, amount) VALUES (?, ?, 0)",
            (user_id, currency_lower)
        )

        cursor.execute(
            "UPDATE balances SET amount = amount + ? WHERE user_id = ? AND currency = ?",
            (amount_change, user_id, currency_lower)
        )

        conn.commit()
        logger.debug(f"Updated balance for user {user_id}: {currency_lower} by {amount_change}")
    except sqlite3.Error as e:
        logger.error(f"Error updating balance for user {user_id}: {e}", exc_info=True)
        conn.rollback()
    finally:
        conn.close()

def transfer_currency(payer_id: int, recipient_id: int, amount: int, currency: str) -> bool:
    """
    Transfers currency from one user to another in a single transaction.
    Returns True on success, False on failure (e.g., insufficient funds).
    """
    if amount <= 0:
        return False

    conn = get_db_connection()
    if not conn:
        return False

    success = False
    try:
        cursor = conn.cursor()
        currency_lower = currency.lower()

        _ensure_user_exists(cursor, payer_id)
        _ensure_user_exists(cursor, recipient_id)

        current_balance = get_balance(payer_id, currency_lower)
        if current_balance < amount:
            logger.warning(f"Transfer failed: User {payer_id} has insufficient {currency_lower} ({current_balance} < {amount})")
            return False

        cursor.execute(
            "UPDATE balances SET amount = amount - ? WHERE user_id = ? AND currency = ?",
            (amount, payer_id, currency_lower)
        )
        cursor.execute(
            "INSERT OR IGNORE INTO balances (user_id, currency, amount) VALUES (?, ?, 0)",
            (recipient_id, currency_lower)
        )
        cursor.execute(
            "UPDATE balances SET amount = amount + ? WHERE user_id = ? AND currency = ?",
            (amount, recipient_id, currency_lower)
        )

        conn.commit()
        success = True
        logger.info(f"Successfully transferred {amount} {currency_lower} from {payer_id} to {recipient_id}")
    except sqlite3.Error as e:
        logger.error(f"Error during currency transfer: {e}", exc_info=True)
        conn.rollback()
    finally:
        conn.close()

    return success

# --- Statistics Functions ---

def track_command_usage(command_name: str):
    """
    Increments the usage count for a given command.
    """
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO command_usage (command_name, usage_count) VALUES (?, 1) "
            "ON CONFLICT(command_name) DO UPDATE SET usage_count = usage_count + 1",
            (command_name,)
        )
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Error tracking usage for command '{command_name}': {e}", exc_info=True)
        conn.rollback()
    finally:
        conn.close()

def get_total_users() -> int:
    """
    Returns the total number of unique users who have interacted with the bot.
    """
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

def get_all_command_usage() -> dict[str, int]:
    """
    Returns a dictionary of all commands and their usage counts.
    """
    conn = get_db_connection()
    if not conn:
        return {}

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT command_name, usage_count FROM command_usage")
        rows = cursor.fetchall()
        return {row['command_name']: row['usage_count'] for row in rows}
    except sqlite3.Error as e:
        logger.error(f"Error getting all command usage: {e}", exc_info=True)
        return {}
    finally:
        conn.close()

def reset_all_command_usage():
    """
    Resets all command usage counters to zero.
    """
    conn = get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM command_usage")
        conn.commit()
        logger.warning("All command usage statistics have been reset.")
    except sqlite3.Error as e:
        logger.error(f"Error resetting command usage: {e}", exc_info=True)
        conn.rollback()
    finally:
        conn.close()

