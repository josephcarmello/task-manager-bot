# Development Guide

Complete guide for setting up and running the Task Manager Bot in a local development environment.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Local Development Setup](#local-development-setup)
- [Docker Development Setup](#docker-development-setup)
- [Discord Bot Setup](#discord-bot-setup)
- [Testing Your Changes](#testing-your-changes)
- [Project Structure](#project-structure)
- [Creating a New Cog](#creating-a-new-cog)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Choose one of the following setups:

### Option 1: Local Python Development
- **Python 3.11+** (3.13 recommended)
- **pip** or **pip3**
- **Git**

### Option 2: Docker Development
- **Docker Desktop** or **Docker Engine**
- **Docker Compose**
- **Git**

---

## Quick Start

### Using Docker (Recommended for Testing)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd task-manager-bot

# 2. Copy environment file and add your Discord token
cp .env.example .env
nano .env  # Add your DISCORD_TOKEN

# 3. Start the bot with Docker
docker-compose up

# That's it! Your bot should now be online.
```

### Using Local Python

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd task-manager-bot

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
nano .env  # Add your DISCORD_TOKEN

# 5. Run the bot
python3 main.py
```

---

## Local Development Setup

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd task-manager-bot

# Create a virtual environment
python3 -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your configuration:

```env
# Required
DISCORD_TOKEN=your_discord_bot_token_here

# Optional
LOG_LEVEL=INFO
LOG_LEVEL_COGS=INFO
DATABASE_PATH=task_manager.db
ICON_URL_FOOTER=https://your-icon-url.com/icon.png
```

### 3. Run the Bot

```bash
# Make sure virtual environment is activated
python3 main.py
```

You should see output like:

```
[2025-10-13 10:00:00] [INFO] Logging configured. Main level: INFO
[2025-10-13 10:00:00] [INFO] Core database tables initialized successfully.
[2025-10-13 10:00:01] [INFO] Information Cog v1.0.0 loaded.
[2025-10-13 10:00:01] [INFO] LinkFixer Cog v1.0.0 loaded.
[2025-10-13 10:00:01] [INFO] Stats Cog v1.1.0 loaded.
[2025-10-13 10:00:01] [INFO] Successfully loaded cog: stats
[2025-10-13 10:00:01] [INFO] Logged in as Task Manager#5937
```

### 4. Test in Discord

In your Discord server, try these commands:
- `/info` - Display bot information
- `/stats` - View command usage statistics
- `/balance tokens` - Check token balance
- Post a Twitter/X link - Watch it auto-fix

---

## Docker Development Setup

Docker provides an isolated, consistent environment for development and testing.

### 1. Prerequisites

Install Docker Desktop:
- **macOS**: [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
- **Windows**: [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
- **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)

### 2. Quick Start with Docker

```bash
# Clone repository
git clone <your-repo-url>
cd task-manager-bot

# Copy and configure environment
cp .env.example .env
# Edit .env and add your DISCORD_TOKEN

# Build and run with Docker Compose
docker-compose up --build
```

### 3. Docker Commands

```bash
# Start the bot (foreground)
docker-compose up

# Start the bot (background/detached)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the bot
docker-compose down

# Rebuild after code changes
docker-compose up --build

# Enter the container shell
docker-compose exec bot bash

# View running containers
docker-compose ps
```

### 4. Development Workflow with Docker

```bash
# 1. Make code changes in your editor
# 2. Rebuild and restart
docker-compose down
docker-compose up --build

# Or use this one-liner:
docker-compose down && docker-compose up --build
```

### 5. Docker Volume Persistence

The database is persisted using Docker volumes:
- `./task_manager.db` is mounted to the container
- Your data persists across container restarts
- Delete `task_manager.db` to reset the database

### 6. Docker Development Tips

**Quick rebuild:**
```bash
docker-compose up --build --force-recreate
```

**Clean slate (removes volumes):**
```bash
docker-compose down -v
```

**View container logs:**
```bash
docker-compose logs bot
docker-compose logs -f bot  # Follow mode
```

**Check bot status:**
```bash
docker-compose ps
```

---

## Discord Bot Setup

### 1. Create Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **New Application**
3. Give it a name (e.g., "Task Manager Bot Dev")
4. Click **Create**

### 2. Create Bot User

1. Go to **Bot** section in left sidebar
2. Click **Add Bot** → **Yes, do it!**
3. Under **Token**, click **Reset Token** and copy it
4. Save this token securely - you'll need it for `.env`

### 3. Configure Bot Permissions

In the **Bot** section:
- Enable **Presence Intent**
- Enable **Server Members Intent**
- Enable **Message Content Intent**

### 4. Invite Bot to Test Server

1. Go to **OAuth2** → **URL Generator**
2. Select scopes:
   - ✅ `bot`
   - ✅ `applications.commands`
3. Select bot permissions:
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Read Message History
   - ✅ Manage Messages (for Fixtter cog)
   - ✅ Use Slash Commands
4. Copy the generated URL
5. Open URL in browser and add bot to your test server

### 5. Set Up Test Server Roles

For role-based commands (admin, banker), create these roles in your test server:
- `admin` - For admin commands
- `banker` - For currency management

Configure roles in `roles_config.py`:

```python
ROLE_MAPPINGS = {
    'admin': [123456789],    # Role ID for admin role
    'banker': [987654321],   # Role ID for banker role
}
```

To get role IDs:
1. Enable Developer Mode in Discord (Settings → Advanced → Developer Mode)
2. Right-click role → Copy ID

---

## Testing Your Changes

### Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Test syntax of a specific file
python3 -m py_compile cogs/your_cog/your_cog.py

# Test all cogs
python3 -m py_compile cogs/*/[!_]*.py

# Run the bot
python3 main.py
```

### Testing with Docker

```bash
# Rebuild and run
docker-compose up --build

# Check logs for errors
docker-compose logs -f bot
```

### Manual Testing in Discord

1. Start your bot (local or Docker)
2. In Discord, use your test server
3. Test commands:
   ```
   /info
   /stats
   /balance tokens
   /pay @user 100 tokens
   /award @user 1000 tokens
   ```
4. Test Fixtter by posting: `https://twitter.com/username/status/123`
5. Check logs for any errors

### Checking Linter Errors

```bash
# Check for Python syntax errors
python3 -m py_compile main.py

# Check a specific cog
python3 -m py_compile cogs/information/information.py
```

---

## Project Structure

```
task-manager-bot/
├── main.py                      # Bot entry point
├── logging_config.py            # Logging configuration
├── roles_config.py              # Role permission system
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker image definition
├── docker-compose.yml           # Docker Compose configuration
├── .env                         # Environment variables (create from .env.example)
├── .env.example                 # Environment template
├── task_manager.db              # SQLite database (auto-created)
│
├── database/                    # Shared database functions
│   ├── __init__.py              # Exposes database functions
│   └── core.py                  # Core database functions
│
├── cogs/                        # Bot extensions (cogs)
│   ├── base_cog.py              # Base class for all cogs
│   │
│   ├── information/             # Bot info cog
│   │   ├── information.py
│   │   └── config.json
│   │
│   ├── stats/                   # Statistics tracking cog
│   │   ├── stats.py
│   │   ├── cog_db_functions.py
│   │   └── config.json
│   │
│   ├── central_bank/            # Currency system cog
│   │   ├── central_bank.py
│   │   ├── cog_db_functions.py
│   │   └── config.json
│   │
│   ├── fixtter/                 # Link fixer cog
│   │   ├── fixtter.py
│   │   └── config.json
│   │
│   └── cog_template/            # Template for new cogs
│       ├── cog_template.py
│       ├── cog_db_functions.py
│       └── config.json
│
└── Documentation/
    ├── README.md                # Project overview
    ├── DEVELOPMENT.MD           # This file
    ├── DATABASE_ARCHITECTURE.md # Database usage guide
    └── cogs/
        ├── README.md            # Cogs overview
        ├── BASE_COG_GUIDE.md    # BaseCog usage guide
        ├── QUICK_REFERENCE.md   # Quick reference
        └── ARCHITECTURE.md      # System architecture
```

---

## Creating a New Cog

### Quick Method

```bash
# 1. Copy the template
cp -r cogs/cog_template cogs/my_new_cog

# 2. Rename the main file
cd cogs/my_new_cog
mv cog_template.py my_new_cog.py

# 3. Edit the file and update:
#    - Class name
#    - Version
#    - Commands
#    - setup() function

# 4. Edit config.json with your settings

# 5. Restart the bot
```

### Minimal Cog Example

```python
from discord import app_commands
from discord.ext import commands
from cogs.base_cog import BaseCog

class MyNewCog(BaseCog):
    __version__ = "1.0.0"
    
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
    
    @app_commands.command(name="hello", description="Say hello")
    async def hello(self, interaction: discord.Interaction):
        await self._send_success(interaction, "Hello!", "👋 Hello World!")

async def setup(bot: commands.Bot):
    await bot.add_cog(MyNewCog(bot))
```

For more details, see:
- [BASE_COG_GUIDE.md](BASE_COG_GUIDE.md) - Complete guide
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Cheat sheet
- [Cogs README](README.md) - Cogs overview

---

## Troubleshooting

### Bot Won't Start

**Issue**: `DISCORD_TOKEN environment variable not set`
```bash
# Solution: Create .env file with your token
cp .env.example .env
# Edit .env and add: DISCORD_TOKEN=your_token_here
```

**Issue**: `ModuleNotFoundError: No module named 'discord'`
```bash
# Solution: Install dependencies
pip install -r requirements.txt
```

**Issue**: `ExtensionFailed: Extension 'cogs.xxx' raised an error`
```bash
# Solution: Check the cog for syntax errors
python3 -m py_compile cogs/xxx/xxx.py
# Fix any syntax errors shown
```

### Docker Issues

**Issue**: `docker-compose: command not found`
```bash
# Solution: Install Docker Desktop or docker-compose
# macOS: brew install docker-compose
# Linux: sudo apt-get install docker-compose
```

**Issue**: Container keeps restarting
```bash
# Check logs for errors
docker-compose logs -f bot

# Common causes:
# - Missing DISCORD_TOKEN in .env
# - Syntax error in Python code
# - Invalid Discord token
```

**Issue**: Changes not reflected in container
```bash
# Solution: Rebuild the container
docker-compose down
docker-compose up --build
```

### Discord Issues

**Issue**: Commands not showing in Discord
```bash
# Solution: Wait a few minutes for Discord to sync
# Or restart the bot to force a resync
# Commands can take up to an hour to appear globally
```

**Issue**: Bot is offline
```bash
# Check if bot is running
docker-compose ps  # For Docker
# or check terminal output for errors

# Verify token in .env is correct
# Check bot permissions in Discord Developer Portal
```

**Issue**: `Missing Permissions` error
```bash
# Solution: Update bot permissions
# 1. Go to Discord Developer Portal
# 2. OAuth2 → URL Generator
# 3. Select all required permissions
# 4. Re-invite bot with new URL
```

### Database Issues

**Issue**: Database locked
```bash
# Solution: Close all connections and restart
# With Docker:
docker-compose down
docker-compose up

# Local:
# Kill the Python process and restart
```

**Issue**: Reset database
```bash
# Stop the bot
docker-compose down  # or Ctrl+C

# Delete database
rm task_manager.db

# Restart bot (database will be recreated)
docker-compose up
```

### Development Tips

**View all logs:**
```bash
# Local
python3 main.py  # logs print to console

# Docker
docker-compose logs -f bot
```

**Debug mode:**
```bash
# Set in .env
LOG_LEVEL=DEBUG
LOG_LEVEL_COGS=DEBUG
```

**Hot reload (no restart needed):**
```python
# Use Discord commands (if you implement them)
/reload <cog_name>
/unload <cog_name>
/load <cog_name>
```

**Test database directly:**
```bash
sqlite3 task_manager.db
# Run SQL queries
SELECT * FROM users;
.tables
.exit
```

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DISCORD_TOKEN` | ✅ Yes | - | Your Discord bot token |
| `LOG_LEVEL` | No | `INFO` | Main log level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_LEVEL_COGS` | No | `INFO` | Cog-specific log level |
| `DATABASE_PATH` | No | `task_manager.db` | SQLite database file path |
| `ICON_URL_FOOTER` | No | - | Footer icon URL for embeds |

---

## Additional Resources

- **Discord.py Documentation**: https://discordpy.readthedocs.io/
- **Discord Developer Portal**: https://discord.com/developers/applications
- **Docker Documentation**: https://docs.docker.com/
- **Python Virtual Environments**: https://docs.python.org/3/tutorial/venv.html

---

## Getting Help

1. Check the logs for error messages
2. Review the documentation in `/docs/` directory
3. Search existing GitHub issues
5. Create a new GitHub issue with:
   - Error message
   - Steps to reproduce
   - Your environment (Docker/Local, Python version)
   - Log output

---

## Contributing

When contributing code:

1. Create a new branch: `git checkout -b feature/my-new-feature`
2. Make your changes
3. Test locally with both methods (local Python and Docker)
4. Ensure all cogs load without errors
5. Test your commands in Discord
6. Commit with clear message: `git commit -m "Add new feature"`
7. Push and create a Pull Request

---

**Happy Developing! 🚀**

*Need help? See troubleshooting section or check the documentation in `/docs/`*

