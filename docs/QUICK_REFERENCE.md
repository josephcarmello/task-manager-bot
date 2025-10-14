# BaseCog Quick Reference Card

## Basic Template

```python
from discord import app_commands
from discord.ext import commands
from cogs.base_cog import BaseCog

class MyCog(BaseCog):
    __version__ = "1.0.0"
    
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
    
    @app_commands.command(name="cmd", description="Description")
    async def cmd(self, interaction: discord.Interaction):
        embed = self._create_embed("Title", "Description")
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(MyCog(bot))
```

## Available Attributes

```python
self.bot           # Discord bot instance
self.cog_name      # Auto-detected cog name
self.logger        # Per-cog logger
self.config        # Config dict from config.json
self.db            # Database module (if configured)
self.embed_color   # Color as int from config
```

## Helper Methods

```python
# Create embeds
embed = self._create_embed("Title", "Description")

# Send messages
await self._send_success(interaction, "Success", "Message")
await self._send_error(interaction, "Error", "Message")
await self._handle_db_error(interaction)
```

## Logging

```python
self.logger.debug("Debug message")
self.logger.info("Info message")
self.logger.warning("Warning message")
self.logger.error("Error message", exc_info=True)
```

## Override Methods

```python
# Custom config defaults
def default_config(self) -> dict:
    config = super().default_config()
    config["color"] = "0x3498DB"
    config["my_setting"] = "value"
    return config

# Additional initialization
def _post_init(self):
    self.cache = {}
    self.my_task.start()
```

## Database Usage

```python
# config.json
{
  "database_module": "cog_db_functions"
}

# In commands
if not self.db:
    await self._handle_db_error(interaction)
    return

try:
    self.db.my_function(data)
    await self._send_success(interaction, "Saved", "Success!")
except Exception as e:
    self.logger.error(f"Error: {e}", exc_info=True)
    await self._send_error(interaction, "Error", "Failed!")
```

## Config File Format

```json
{
  "author_name": "Cog Name",
  "author_icon_url": "https://...",
  "footer_text": "Task Manager Bot",
  "footer_icon_url": "",
  "color": "0x3498DB",
  "log_level": "INFO",
  "database_module": "cog_db_functions"
}
```

## Colors

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

## Create New Cog (3 Steps)

```bash
# 1. Copy template
cp -r cogs/cog_template cogs/my_cog

# 2. Rename file
cd cogs/my_cog
mv cog_template.py my_cog.py

# 3. Edit class name and commands in my_cog.py
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

### Command with args
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

## Documentation Files

- `base_cog.py` - Base class source code
- `BASE_COG_GUIDE.md` - Comprehensive guide
- `QUICK_REFERENCE.md` - This file (cheat sheet)
- `ARCHITECTURE.md` - System architecture diagrams
- `README.md` - Cogs overview

## Example Cogs

- `cog_template/cog_template.py` - Template for new cogs
- `information/information.py` - Simple command example
- `stats/stats.py` - Database integration example
- `central_bank/central_bank.py` - Complex cog example
- `fixtter/fixtter.py` - Event listener example

---

**Tip**: Keep this file open while developing cogs! 📌

