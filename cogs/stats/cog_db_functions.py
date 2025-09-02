# Database functions specific to the Stats cog.
import logging
from database import core

logger = logging.getLogger(__name__)

def initialize_tables():
    """Creates the necessary tables for the Stats cog."""
    conn = core.get_db_connection()
    if not conn:
        logger.error("Could not establish database connection for Stats table initialization.")
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_usage (
                command_name TEXT PRIMARY KEY,
                usage_count INTEGER DEFAULT 0
            )
        """)
        conn.commit()
        logger.info("Stats database tables initialized.")
    except Exception as e:
        logger.error(f"Error initializing Stats tables: {e}", exc_info=True)
    finally:
        conn.close()

def track_command_usage(command_name: str):
    """Increments the usage count for a given command."""
    conn = core.get_db_connection()
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
    except Exception as e:
        logger.error(f"Error tracking usage for command '{command_name}': {e}", exc_info=True)
        conn.rollback()
    finally:
        conn.close()

def get_all_command_usage() -> dict[str, int]:
    """Returns a dictionary of all commands and their usage counts."""
    conn = core.get_db_connection()
    if not conn:
        return {}

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT command_name, usage_count FROM command_usage")
        rows = cursor.fetchall()
        return {row['command_name']: row['usage_count'] for row in rows}
    except Exception as e:
        logger.error(f"Error getting all command usage: {e}", exc_info=True)
        return {}
    finally:
        conn.close()

def reset_all_command_usage():
    """Resets all command usage counters to zero."""
    conn = core.get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM command_usage")
        conn.commit()
        logger.warning("All command usage statistics have been reset.")
    except Exception as e:
        logger.error(f"Error resetting command usage: {e}", exc_info=True)
        conn.rollback()
    finally:
        conn.close()

