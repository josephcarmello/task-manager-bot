# Cog Architecture - System Design

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Task Manager Bot                             │
│                              (main.py)                               │
└───────────────────────────┬─────────────────────────────────────────┘
                            │
                            │ loads cogs
                            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Cog System                                   │
└─────────────────────────────────────────────────────────────────────┘
         │              │              │              │
         ▼              ▼              ▼              ▼
    ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
    │  Stats  │   │  Info   │   │ Central │   │ Fixtter │
    │   Cog   │   │   Cog   │   │  Bank   │   │   Cog   │
    └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘
         │              │              │              │
         └──────────────┴──────────────┴──────────────┘
                            │
                    all inherit from
                            │
                            ▼
                   ┌──────────────┐
                   │   BaseCog    │
                   │ (base_cog.py)│
                   └──────────────┘
```

## BaseCog Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                            BaseCog                                  │
│                        (base_cog.py)                                │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Initialization Flow:                                              │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  1. __init__(bot, cog_name)                                  │ │
│  │     │                                                         │ │
│  │     ├─► 2. _load_config()                                    │ │
│  │     │      ├─► Read config.json                              │ │
│  │     │      ├─► Merge with default_config()                   │ │
│  │     │      └─► Set self.config                               │ │
│  │     │                                                         │ │
│  │     ├─► 3. _setup_logging()                                  │ │
│  │     │      ├─► Get log level from config                     │ │
│  │     │      └─► Configure self.logger                         │ │
│  │     │                                                         │ │
│  │     ├─► 4. _load_db_module()                                 │ │
│  │     │      ├─► Import database module                        │ │
│  │     │      ├─► Call initialize_tables()                      │ │
│  │     │      └─► Set self.db                                   │ │
│  │     │                                                         │ │
│  │     └─► 5. _post_init()                                      │ │
│  │            └─► Hook for child classes                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Provided Attributes:                                              │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  • self.bot          - Discord bot instance                  │ │
│  │  • self.cog_name     - Auto-detected cog name                │ │
│  │  • self.logger       - Per-cog logger                        │ │
│  │  • self.config       - Configuration dictionary              │ │
│  │  • self.db           - Database module (optional)            │ │
│  │  • self.embed_color  - Embed color as int                    │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Provided Methods:                                                 │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  • _create_embed(title, desc)                                │ │
│  │  • _send_success(interaction, title, msg)                    │ │
│  │  • _send_error(interaction, title, msg)                      │ │
│  │  • _handle_db_error(interaction, msg)                        │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Override Hooks:                                                   │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  • default_config()  - Provide custom defaults               │ │
│  │  • _post_init()      - Additional initialization             │ │
│  └──────────────────────────────────────────────────────────────┘ │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

## Cog Inheritance Pattern

```
                    ┌──────────────┐
                    │ commands.Cog │
                    │ (Discord.py) │
                    └───────┬──────┘
                            │
                            │ inherits
                            ▼
                    ┌──────────────┐
                    │   BaseCog    │
                    │ (base_cog.py)│
                    └───────┬──────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
            ▼               ▼               ▼
       ┌─────────┐     ┌─────────┐    ┌─────────┐
       │StatsCog │     │InfoCog  │    │YourCog  │
       └─────────┘     └─────────┘    └─────────┘
```

## Configuration Loading Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   Configuration Loading                          │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────┐
        │ Does config.json exist?           │
        └───────┬───────────────────┬───────┘
                │ YES               │ NO
                ▼                   ▼
    ┌──────────────────┐   ┌──────────────────┐
    │ Load config.json │   │ Use defaults     │
    └────────┬─────────┘   └────────┬─────────┘
             │                      │
             └──────────┬───────────┘
                        │
                        ▼
        ┌───────────────────────────────────┐
        │ Merge with default_config()       │
        │ (fills in missing keys)           │
        └────────────────┬──────────────────┘
                         │
                         ▼
        ┌───────────────────────────────────┐
        │ Apply environment variable        │
        │ fallbacks (e.g., ICON_URL_FOOTER) │
        └────────────────┬──────────────────┘
                         │
                         ▼
                 ┌──────────────┐
                 │ self.config  │
                 │   (ready!)   │
                 └──────────────┘
```

## Database Module Loading Flow

```
┌─────────────────────────────────────────────────────────────────┐
│              Database Module Loading (Optional)                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
        ┌───────────────────────────────────────┐
        │ Is "database_module" in config?       │
        └───────┬───────────────────────┬───────┘
                │ YES                   │ NO
                ▼                       ▼
    ┌──────────────────────┐   ┌──────────────┐
    │ Import module        │   │ self.db=None │
    │ cogs.cogname.modname │   └──────────────┘
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │ Has initialize_tables│
    │ function?            │
    └──────────┬───────────┘
               │ YES
               ▼
    ┌──────────────────────┐
    │ Call                 │
    │ initialize_tables()  │
    └──────────┬───────────┘
               │
               ▼
       ┌──────────────┐
       │ self.db      │
       │ (ready!)     │
       └──────────────┘
```

## Command Execution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Interaction                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Discord.py     │
                    │ routes command │
                    └────────┬───────┘
                             │
                             ▼
                    ┌────────────────┐
                    │ Your Cog       │
                    │ @app_commands  │
                    │ .command()     │
                    └────────┬───────┘
                             │
                             ▼
               ┌─────────────────────────┐
               │ Your command function   │
               │ (has access to:)        │
               ├─────────────────────────┤
               │ • self.logger           │
               │ • self.config           │
               │ • self.db               │
               │ • self._create_embed()  │
               │ • self._send_success()  │
               │ • self._send_error()    │
               └─────────────────────────┘
```

## File Structure

```
cogs/
│
├── base_cog.py ⭐                    # Base class
│
├── your_cog/                         # Your cog directory
│   ├── __init__.py                   # (optional)
│   ├── your_cog.py                   # Main cog file
│   ├── config.json                   # Configuration
│   └── cog_db_functions.py          # (optional) Database functions
│
├── Documentation
│   ├── BASE_COG_GUIDE.md            # Complete guide
│   ├── QUICK_REFERENCE.md           # Cheat sheet
│   └── ARCHITECTURE.md              # This file
│
└── Examples
    ├── information/information.py    # Simple cog
    ├── stats/stats.py                # Cog with database
    ├── central_bank/central_bank.py  # Complex cog
    ├── fixtter/fixtter.py            # Event listener
    └── cog_template/cog_template.py  # Template for new cogs
```

## Data Flow Diagram

```
┌─────────────┐
│   User      │
│ /command    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         Discord.py                       │
│    (handles Discord protocol)            │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         Bot (main.py)                    │
│    (routes to correct cog)               │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│         YourCog (BaseCog)                │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │ Your command function              │ │
│  ├────────────────────────────────────┤ │
│  │ 1. Log with self.logger            │ │
│  │ 2. Check self.db if needed         │ │
│  │ 3. Create embed                    │ │
│  │ 4. Send response                   │ │
│  └────────────────────────────────────┘ │
│                                          │
│  Uses BaseCog methods:                  │
│  • self._create_embed()                 │
│  • self._send_success()                 │
│  • self._send_error()                   │
│                                          │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│      Database (optional)                 │
│  (SQLite via cog_db_functions.py)       │
└─────────────────────────────────────────┘
```

## Extension Points

BaseCog provides multiple extension points for customization:

```
BaseCog
│
├─► default_config()
│   └─ Override to provide custom defaults
│
├─► _post_init()
│   └─ Override for additional initialization
│
├─► _load_config()
│   └─ Override for custom config loading logic
│       (not recommended, but possible)
│
├─► _setup_logging()
│   └─ Override for custom logging setup
│       (not recommended, but possible)
│
└─► Any other method
    └─ All methods can be overridden if needed
```

## Best Practices

```
DO ✅
├─ Inherit from BaseCog for all new cogs
├─ Use self.logger for logging
├─ Use helper methods (_send_success, etc.)
├─ Override default_config() for custom defaults
├─ Use _post_init() for additional setup
└─ Keep cogs focused on one responsibility

DON'T ❌
├─ Don't reimplement base methods
├─ Don't use module-level loggers
├─ Don't duplicate configuration logic
├─ Don't skip error handling
└─ Don't create mega-cogs with too many features
```

## Creating a New Cog

```bash
# 1. Copy template
cp -r cogs/cog_template cogs/my_cog

# 2. Rename file
cd cogs/my_cog
mv cog_template.py my_cog.py

# 3. Edit my_cog.py
# - Change class name
# - Update __version__
# - Add your commands
# - Update setup() function

# 4. Edit config.json
# - Set cog name, colors, etc.

# 5. Restart bot
python main.py
```

## Minimal Working Cog

```python
from discord import app_commands
from discord.ext import commands
from cogs.base_cog import BaseCog

class MyCog(BaseCog):
    __version__ = "1.0.0"
    
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
    
    @app_commands.command(name="test", description="Test")
    async def test(self, interaction: discord.Interaction):
        await self._send_success(interaction, "Test", "Works! ✅")

async def setup(bot: commands.Bot):
    await bot.add_cog(MyCog(bot))
```
