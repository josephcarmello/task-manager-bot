# BaseCog Guide - Creating Discord Cogs

## Overview

The `BaseCog` class provides a foundation for all cogs in the Task Manager Bot. It handles common functionality like configuration loading, logging setup, database integration, and Discord embed creation.

## Benefits

✅ **Minimal boilerplate** - Just inherit and add your commands  
✅ **Consistent behavior** across all cogs  
✅ **Automatic configuration** loading from config.json  
✅ **Built-in logging** with per-cog loggers  
✅ **Database integration** (optional)  
✅ **Helper methods** for common tasks  

## Quick Start

### Creating a New Cog (3 Steps)

**1. Copy the cog_template folder**
```bash
cp -r cogs/cog_template cogs/my_new_cog
```

**2. Rename and edit the main file**
```bash
cd cogs/my_new_cog
mv cog_template.py my_new_cog.py
```

**3. Update the class and commands**
```python
from cogs.base_cog import BaseCog
from discord import app_commands
from discord.ext import commands

class MyNewCog(BaseCog):
    __version__ = "1.0.0"

    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
    
    # Add your commands here
    @app_commands.command(name="mycommand", description="Does something cool.")
    async def mycommand(self, interaction: discord.Interaction):
        embed = self._create_embed("My Command", "It works!")
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(MyNewCog(bot))
```

That's it! Your cog is ready to use.

## Architecture

### What BaseCog Provides

```
BaseCog
├── Automatic Configuration Loading
│   ├── Loads config.json from cog directory
│   ├── Merges with sensible defaults
│   └── Environment variable fallbacks
│
├── Logging Setup
│   ├── Per-cog logger instance (self.logger)
│   ├── Configurable log levels
│   └── Automatic log level detection
│
├── Database Module Loading (Optional)
│   ├── Dynamic import based on config
│   ├── Automatic table initialization
│   └── Available as self.db
│
├── Discord Embed Creation
│   ├── Standardized styling
│   ├── Consistent branding
│   └── Configured from config.json
│
└── Helper Methods
    ├── Error handling
    ├── Success messages
    └── DB error messages
```

## Basic Example

```python
from discord import app_commands
from discord.ext import commands
from cogs.base_cog import BaseCog

class MyCog(BaseCog):
    __version__ = "1.0.0"
    
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
    
    @app_commands.command(name="test", description="Test command")
    async def test(self, interaction: discord.Interaction):
        embed = self._create_embed("Test", "Works!")
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(MyCog(bot))
```

## Available Features

### Attributes

All cogs inheriting from `BaseCog` have access to:

| Attribute | Type | Description |
|-----------|------|-------------|
| `self.bot` | `commands.Bot` | The Discord bot instance |
| `self.cog_name` | `str` | Auto-detected cog name |
| `self.logger` | `logging.Logger` | Per-cog logger instance |
| `self.config` | `dict` | Configuration dictionary |
| `self.db` | `module or None` | Database module (if configured) |
| `self.embed_color` | `int` | Embed color from config |

### Methods

| Method | Description |
|--------|-------------|
| `default_config()` | Override to provide custom default config |
| `_post_init()` | Override for additional initialization |
| `_create_embed(title, desc)` | Create standardized embeds |
| `_send_success(interaction, title, msg)` | Send success embed |
| `_send_error(interaction, title, msg)` | Send error embed |
| `_handle_db_error(interaction, msg)` | Handle database errors |

## Advanced Usage

### 1. Custom Configuration Defaults

Override `default_config()` to provide custom defaults:

```python
class MyCog(BaseCog):
    def default_config(self) -> dict:
        config = super().default_config()
        config["color"] = "0x3498DB"  # Blue
        config["author_name"] = "My Custom Cog"
        config["api_endpoint"] = "https://api.example.com"
        return config
```

### 2. Additional Initialization

Use `_post_init()` for custom setup after base initialization:

```python
from discord.ext import tasks

class MyCog(BaseCog):
    def _post_init(self):
        """Called after config, logging, and DB are set up."""
        self.cache = {}
        self.api_client = APIClient(self.config.get("api_endpoint"))
        self.background_task.start()
    
    @tasks.loop(hours=1)
    async def background_task(self):
        self.logger.info("Running background task")
        # Do background work
```

### 3. Database Integration

Configure in `config.json`:
```json
{
  "database_module": "cog_db_functions"
}
```

Use in your cog:
```python
@app_commands.command(name="save", description="Save data")
async def save(self, interaction: discord.Interaction, data: str):
    if not self.db:
        await self._handle_db_error(interaction)
        return
    
    try:
        self.db.save_user_data(interaction.user.id, data)
        await self._send_success(interaction, "Saved", "Data saved!")
    except Exception as e:
        self.logger.error(f"Error: {e}", exc_info=True)
        await self._send_error(interaction, "Error", "Save failed")
```

### 4. Using Helper Methods

BaseCog provides several helper methods:

```python
# Create embeds
embed = self._create_embed("Title", "Description")

# Send success messages
await self._send_success(interaction, "Success", "Operation completed")

# Send error messages
await self._send_error(interaction, "Error", "Something went wrong")

# Handle DB errors
await self._handle_db_error(interaction)
await self._handle_db_error(interaction, "Custom error message")
```

### 5. Logging

Each cog gets its own logger:

```python
self.logger.debug("Debug message")
self.logger.info("Info message")
self.logger.warning("Warning message")
self.logger.error("Error message", exc_info=True)
```

## Configuration File (config.json)

Place in your cog's directory:

```json
{
  "author_name": "My Cog Name",
  "author_icon_url": "https://example.com/icon.png",
  "footer_text": "Task Manager Bot",
  "footer_icon_url": "",
  "color": "0x3498DB",
  "log_level": "INFO",
  "database_module": "cog_db_functions"
}
```

All fields are optional with sensible defaults.

### Common Colors

```
0x1ABC9C  # Turquoise
0x2ECC71  # Green
0x3498DB  # Blue
0x9B59B6  # Purple
0xE74C3C  # Red
0xE67E22  # Orange
0xF1C40F  # Yellow
0x95A5A6  # Gray
0xECF0F1  # Light Gray
```

## Common Patterns

### Admin-only command
```python
import roles_config

@app_commands.command(name="admin", description="[Admin Only] Command")
@roles_config.has_role('admin')
async def admin_cmd(self, interaction: discord.Interaction):
    await self._send_success(interaction, "Done", "Success")
```

### Command with arguments
```python
@app_commands.command(name="greet", description="Greet someone")
@app_commands.describe(name="Name to greet", times="Times to greet")
async def greet(self, interaction: discord.Interaction, name: str, times: int = 1):
    message = f"Hello {name}! " * times
    await self._send_success(interaction, "Greeting", message)
```

### Background task
```python
from discord.ext import tasks

def _post_init(self):
    self.cleanup.start()

@tasks.loop(hours=1)
async def cleanup(self):
    self.logger.info("Running cleanup")
    # Cleanup code here
```

### Event listener
```python
@commands.Cog.listener()
async def on_message(self, message: discord.Message):
    if message.author == self.bot.user:
        return
    self.logger.debug(f"Message from {message.author}")
```

## Design Principles

1. **Convention over Configuration** - Sensible defaults for everything
2. **Extensibility** - Override anything you need
3. **Consistency** - All cogs behave the same way
4. **Simplicity** - Focus on features, not boilerplate

## Testing Your Cog

```python
# Minimal test cog
class TestCog(BaseCog):
    __version__ = "1.0.0"
    
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
    
    @app_commands.command(name="test", description="Test command")
    async def test(self, interaction: discord.Interaction):
        self.logger.info(f"Test by {interaction.user}")
        await self._send_success(interaction, "Test", "It works! ✅")

async def setup(bot: commands.Bot):
    await bot.add_cog(TestCog(bot))
```

## Troubleshooting

### Config not loading?
- Check that `config.json` exists in your cog's directory
- Override `default_config()` to provide defaults
- Check logs for error messages

### Logger not working?
- Use `self.logger` instead of module-level `logger`
- Check log level in config.json or LOG_LEVEL_COGS env var

### Database not loading?
- Set `"database_module": "cog_db_functions"` in config.json
- Ensure your DB module has `initialize_tables()` function
- Check `self.db` is not None before using

## Examples

See existing cogs for real-world examples:
- `information/information.py` - Simple cog with commands
- `stats/stats.py` - Cog with database integration
- `central_bank/central_bank.py` - Complex cog with role permissions
- `fixtter/fixtter.py` - Event listener cog

## Quick Reference

See [QUICK_REFERENCE.md](QUICK_REFERENCE.md) for a cheat sheet!

---

*For system architecture, see [ARCHITECTURE.md](ARCHITECTURE.md)*  
*For database usage, see [DATABASE_ARCHITECTURE.md](DATABASE_ARCHITECTURE.md)*
