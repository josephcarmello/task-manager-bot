"""
Database Module - Provides shared database functionality for all cogs.

This module exposes:
- Core database functions (from database.core)
- Currency functions (from central_bank cog)
- Command tracking (from stats cog)

Any cog can import this module to access shared database functionality:
    import database
    balance = database.get_balance(user_id, "tokens")
"""

# Import and expose core database functions
from database.core import (
    get_db_connection,
    initialize_database,
    get_total_users
)

# Import and expose currency functions from central_bank
from cogs.central_bank.cog_db_functions import (
    initialize_tables as initialize_currency_tables,
    get_balance,
    update_balance,
    transfer_currency
)

# Import and expose stats tracking functions
from cogs.stats.cog_db_functions import (
    track_command_usage
)

__all__ = [
    # Core functions
    'get_db_connection',
    'initialize_database',
    'get_total_users',
    
    # Currency functions
    'initialize_currency_tables',
    'get_balance',
    'update_balance',
    'transfer_currency',
    
    # Stats functions
    'track_command_usage',
]

