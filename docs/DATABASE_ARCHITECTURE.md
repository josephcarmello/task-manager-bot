# Database Architecture - Shared Currency System

## Overview

The Task Manager Bot uses a **shared database architecture** where currency functions are accessible by all cogs, not just the Central Bank cog.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Database Module                           │
│                  (database/__init__.py)                      │
│                                                              │
│  Exposes shared functions from multiple sources:            │
│  ├─ Core functions (database/core.py)                       │
│  ├─ Currency functions (central_bank/cog_db_functions.py)   │
│  └─ Stats tracking (stats/cog_db_functions.py)              │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Available to
                            ▼
        ┌───────────────────────────────────────┐
        │         All Cogs Can Access           │
        ├───────────────────────────────────────┤
        │  • Central Bank Cog (UI commands)     │
        │  • Stats Cog (tracking)               │
        │  • Information Cog (if needed)        │
        │  • Any future cog                     │
        └───────────────────────────────────────┘
```

## Database Tables

### Core Tables (database/core.py)
- **`users`** - Shared table of all Discord users
  - `user_id` (PRIMARY KEY)

### Currency Tables (central_bank/cog_db_functions.py)
- **`balances`** - User currency balances
  - `user_id` (FK to users)
  - `currency` (text: "tokens", "credits", etc.)
  - `amount` (integer)
  - PRIMARY KEY: (user_id, currency)

### Stats Tables (stats/cog_db_functions.py)
- **`command_usage`** - Command usage tracking
  - `command_name` (PRIMARY KEY)
  - `usage_count` (integer)

## Using Currency Functions in Any Cog

### Available Functions

```python
import database

# Get a user's balance
balance = database.get_balance(user_id, "tokens")
# Returns: int (balance amount, 0 if not found)

# Update a user's balance (add or subtract)
database.update_balance(user_id, "tokens", amount_change)
# amount_change can be positive (add) or negative (subtract)

# Transfer currency between users
success = database.transfer_currency(payer_id, recipient_id, amount, "tokens")
# Returns: bool (True if successful, False if insufficient funds)

# Track command usage (for stats)
database.track_command_usage("command_name")
```

### Example: Using Currency in Your Cog

```python
from discord import app_commands
from discord.ext import commands
from cogs.base_cog import BaseCog
import database  # ← Import the shared database module


class MyRewardsCog(BaseCog):
    """Example cog that uses the currency system."""
    __version__ = "1.0.0"

    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
    
    @app_commands.command(name="daily-reward", description="Claim your daily tokens!")
    async def daily_reward(self, interaction: discord.Interaction):
        """Give users 100 tokens per day."""
        user_id = interaction.user.id
        reward_amount = 100
        
        # Award tokens to the user
        database.update_balance(user_id, "tokens", reward_amount)
        
        # Check their new balance
        new_balance = database.get_balance(user_id, "tokens")
        
        await self._send_success(
            interaction,
            "Daily Reward Claimed! 🎁",
            f"You received {reward_amount} tokens!\n"
            f"Your new balance: {new_balance} tokens"
        )
    
    @app_commands.command(name="buy-item", description="Buy an item with tokens")
    @app_commands.describe(item_name="The item to buy")
    async def buy_item(self, interaction: discord.Interaction, item_name: str):
        """Example of spending currency."""
        user_id = interaction.user.id
        item_cost = 500  # Items cost 500 tokens
        
        # Check if user has enough tokens
        current_balance = database.get_balance(user_id, "tokens")
        
        if current_balance < item_cost:
            await self._send_error(
                interaction,
                "Insufficient Tokens",
                f"You need {item_cost} tokens but only have {current_balance}."
            )
            return
        
        # Deduct the cost (negative amount)
        database.update_balance(user_id, "tokens", -item_cost)
        
        await self._send_success(
            interaction,
            "Purchase Complete! 🛒",
            f"You bought {item_name} for {item_cost} tokens!"
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(MyRewardsCog(bot))
```

## Central Bank Cog Role

The **Central Bank cog** provides the **user interface** for the currency system:
- `/balance` - Check currency balance
- `/pay` - Transfer currency to another user
- `/award` - [Admin] Award currency to users

**But the currency data is shared!** Any cog can:
- Read balances
- Update balances
- Transfer currency
- Create new currencies

## Multiple Currencies

The system supports **unlimited currencies**:
- `tokens`
- `credits`
- `gold`
- `reputation`
- `xp`
- ... anything you want!

Just use a different currency name:
```python
database.get_balance(user_id, "gold")
database.update_balance(user_id, "reputation", 10)
database.transfer_currency(user1, user2, 50, "xp")
```

## Initialization

Currency tables are initialized at bot startup in `main.py`:

```python
if __name__ == "__main__":
    # Initialize core tables (users)
    db_core.initialize_database()
    
    # Initialize currency tables (balances)
    import database
    database.initialize_currency_tables()
    
    # Start bot
    bot = TaskManagerBot()
    bot.run(DISCORD_TOKEN)
```

## Best Practices

### ✅ Do This
- Import `database` module in any cog that needs currency
- Use `database.get_balance()` to check before spending
- Use negative amounts with `update_balance()` to deduct currency
- Use `transfer_currency()` for user-to-user transfers (it validates automatically)
- Log currency transactions with `self.logger`

### ❌ Don't Do This
- Don't directly query the database with SQL (use the provided functions)
- Don't create negative balances (functions prevent this)
- Don't bypass the currency functions (they include validation)
- Don't forget to check balances before deductions

## Transaction Safety

All currency functions include:
- ✅ **User validation** - Creates users if they don't exist
- ✅ **Balance validation** - Prevents negative balances
- ✅ **Atomic operations** - Uses database transactions
- ✅ **Error handling** - Returns False/0 on errors (doesn't crash)
- ✅ **Logging** - Logs all errors for debugging

## Example Use Cases

### Economy System
```python
# Daily rewards
database.update_balance(user_id, "tokens", 100)

# Shop purchases
database.update_balance(user_id, "tokens", -item_cost)

# Gambling
winner_id = determine_winner()
database.transfer_currency(loser_id, winner_id, bet_amount, "tokens")
```

### Reputation System
```python
# Upvote someone
database.update_balance(target_user_id, "reputation", 1)

# Downvote someone
database.update_balance(target_user_id, "reputation", -1)

# Check reputation
rep = database.get_balance(user_id, "reputation")
```

### XP/Leveling System
```python
# Award XP for messages
database.update_balance(user_id, "xp", 10)

# Check level
xp = database.get_balance(user_id, "xp")
level = xp // 100  # 100 XP per level

# Level up rewards
if xp % 100 == 0:  # Just leveled up
    database.update_balance(user_id, "tokens", 500)
```

## Summary

**Yes, the Central Bank currency system is accessible by ALL cogs!**

- ✅ Import `database` module
- ✅ Use `get_balance()`, `update_balance()`, `transfer_currency()`
- ✅ Any cog can read/write currency data
- ✅ Central Bank cog is just the UI
- ✅ Currency data is shared across all cogs
- ✅ Supports unlimited currency types

This architecture allows you to build complex economy systems, reward systems, reputation systems, and more - all using the same shared currency infrastructure! 🚀

---

*See `database/__init__.py` for all available functions*  
*See `cogs/central_bank/cog_db_functions.py` for implementation details*

