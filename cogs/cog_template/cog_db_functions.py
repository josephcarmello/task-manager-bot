# This is a template file for a new cog's database functions.
import logging
from database import core

logger = logging.getLogger(__name__)

def initialize_tables():
    """Creates the necessary tables for this cog."""
    conn = core.get_db_connection()
    if not conn:
        logger.error("Could not establish database connection for table initialization.")
        return
    try:
        cursor = conn.cursor()
        # TODO: Add your CREATE TABLE statement(s) here
        # cursor.execute("""
        #     CREATE TABLE IF NOT EXISTS my_table (
        #         id INTEGER PRIMARY KEY,
        #         data TEXT NOT NULL
        #     )
        # """)
        conn.commit()
        logger.info("Template Cog database tables initialized.")
    except Exception as e:
        logger.error(f"Error initializing Template Cog tables: {e}", exc_info=True)
    finally:
        conn.close()

# --- Add your cog-specific database functions below ---

# def get_my_data(user_id: int):
#     """Example function to get data."""
#     pass

# def save_my_data(user_id: int, data: str):
#     """Example function to save data."""
#     pass

