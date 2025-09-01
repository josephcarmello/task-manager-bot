import sqlite3
import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)

DB_PATH = os.getenv('DATABASE_PATH', 'task_manager.db')

def initialize_database():
    """
    Initializes the database and creates tables if they don't exist.
    This function should be called ONCE when the bot starts.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Table for user balances (supports multiple currencies)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS balances (
                    user_id INTEGER NOT NULL,
                    currency TEXT NOT NULL,
                    amount REAL NOT NULL,
                    PRIMARY KEY (user_id, currency)
                )
            ''')

            # Table for tracking command usage statistics
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS command_stats (
                    command_name TEXT PRIMARY KEY,
                    usage_count INTEGER NOT NULL DEFAULT 0
                )
            ''')

            conn.commit()
        logger.info(f"Database initialized successfully at '{DB_PATH}'.")
    except sqlite3.Error as e:
        logger.critical(f"Database initialization failed: {e}", exc_info=True)
        raise

def get_balance(user_id: int, currency: str) -> float:
    """Retrieves a user's balance for a specific currency."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT amount FROM balances WHERE user_id = ? AND currency = ?", (user_id, currency))
            result = cursor.fetchone()
            return float(result[0]) if result else 0.0
    except sqlite3.Error as e:
        logger.error(f"Failed to get balance for user {user_id} ({currency}): {e}", exc_info=True)
        return 0.0

def update_balance(user_id: int, currency: str, amount_change: float):
    """
    Updates a user's balance for a specific currency by a given amount.
    Can be a positive (add) or negative (subtract) amount.
    """
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            current_balance = get_balance(user_id, currency)
            new_balance = current_balance + amount_change

            cursor.execute('''
                INSERT OR REPLACE INTO balances (user_id, currency, amount)
                VALUES (?, ?, ?)
            ''', (user_id, currency, new_balance))
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Failed to update balance for user {user_id} ({currency}): {e}", exc_info=True)
        raise

def track_command_usage(command_name: str):
    """Increments the usage count for a given command."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT OR IGNORE INTO command_stats (command_name, usage_count) VALUES (?, 0)", (command_name,))
            cursor.execute("UPDATE command_stats SET usage_count = usage_count + 1 WHERE command_name = ?", (command_name,))
            conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Failed to track usage for command '{command_name}': {e}", exc_info=True)

def get_all_command_stats() -> Dict[str, int]:
    """Retrieves all command usage stats as a dictionary."""
    stats = {}
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT command_name, usage_count FROM command_stats")
            for row in cursor.fetchall():
                stats[row[0]] = row[1]
    except sqlite3.Error as e:
        logger.error(f"Failed to retrieve command stats: {e}", exc_info=True)
    return stats

def reset_all_command_stats():
    """Resets all command usage counts to 0."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE command_stats SET usage_count = 0")
            conn.commit()
        logger.warning("All command statistics have been reset.")
    except sqlite3.Error as e:
        logger.error(f"Failed to reset command stats: {e}", exc_info=True)
        raise


