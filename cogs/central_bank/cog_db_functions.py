import logging
from database import core

logger = logging.getLogger(__name__)

def initialize_tables():
    """Creates the necessary tables for the Central Bank cog."""
    conn = core.get_db_connection()
    if not conn:
        logger.error("Could not establish database connection for Central Bank table initialization.")
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS balances (
                user_id INTEGER,
                currency TEXT,
                amount INTEGER DEFAULT 0,
                PRIMARY KEY (user_id, currency),
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        logger.info("Central Bank database tables initialized.")
    except Exception as e:
        logger.error(f"Error initializing Central Bank tables: {e}", exc_info=True)
    finally:
        conn.close()


def get_balance(user_id: int, currency: str) -> int:
    """
    Retrieves the balance of a specific currency for a user.
    Creates the user and their balance entry if they don't exist.
    """
    conn = core.get_db_connection()
    balance = 0
    if not conn:
        return balance

    try:
        cursor = conn.cursor()
        core._ensure_user_exists(cursor, user_id)

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
    except Exception as e:
        logger.error(f"Error getting balance for user {user_id}: {e}", exc_info=True)
        conn.rollback()
    finally:
        conn.close()

    return balance

def update_balance(user_id: int, currency: str, amount_change: int):
    """
    Updates a user's balance by a certain amount (can be positive or negative).
    """
    conn = core.get_db_connection()
    if not conn:
        return

    try:
        cursor = conn.cursor()
        core._ensure_user_exists(cursor, user_id)

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
    except Exception as e:
        logger.error(f"Error updating balance for user {user_id}: {e}", exc_info=True)
        conn.rollback()
    finally:
        conn.close()

def transfer_currency(payer_id: int, recipient_id: int, amount: int, currency: str) -> bool:
    """
    Transfers currency from one user to another in a single transaction.
    """
    if amount <= 0:
        return False

    conn = core.get_db_connection()
    if not conn:
        return False

    success = False
    try:
        cursor = conn.cursor()
        currency_lower = currency.lower()

        core._ensure_user_exists(cursor, payer_id)
        core._ensure_user_exists(cursor, recipient_id)

        cursor.execute(
            "SELECT amount FROM balances WHERE user_id = ? AND currency = ?",
            (payer_id, currency_lower)
        )
        result = cursor.fetchone()
        current_balance = result['amount'] if result else 0

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
    except Exception as e:
        logger.error(f"Error during currency transfer: {e}", exc_info=True)
        conn.rollback()
    finally:
        conn.close()

    return success

