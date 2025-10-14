# Task Manager Bot

Who up managing they tasks?

## Quick Start

### Using Docker (Recommended)

```bash
git clone <repo-url>
cd task-manager-bot
cp env.example .env
# Edit .env and add your DISCORD_TOKEN
docker-compose up
```

### Using Python

```bash
git clone <repo-url>
cd task-manager-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env
# Edit .env and add your DISCORD_TOKEN
python3 main.py
```

**[→ Full Quick Start Guide](docs/QUICKSTART.md)**

## Documentation

**[📚 Full Documentation Index →](docs/INDEX.md)**

| Document | Description |
|----------|-------------|
| **[QUICKSTART.md](docs/QUICKSTART.md)** | Get started in 5 minutes |
| **[DEVELOPMENT.MD](docs/DEVELOPMENT.MD)** | Complete development guide |
| **[DOCKER.md](docs/DOCKER.md)** | Docker setup and usage |
| **[DATABASE_ARCHITECTURE.md](docs/DATABASE_ARCHITECTURE.md)** | Database and currency system |
| **[Cogs README](docs/README.md)** | Creating and managing cogs |
| **[BASE_COG_GUIDE.md](docs/BASE_COG_GUIDE.md)** | BaseCog usage guide |
| **[QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** | Developer cheat sheet |
| **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** | System architecture |

## Requirements

- **Python 3.11+** (3.13 recommended)
- **Discord.py 2.6+**
- **SQLite** (included with Python)

Or use **Docker** (no Python installation needed)

## Creating a New Cog

```bash
# 1. Copy the template
cp -r cogs/cog_template cogs/my_cog

# 2. Rename and edit
cd cogs/my_cog
mv cog_template.py my_cog.py
# Edit my_cog.py and add your commands

# 3. Restart bot
docker-compose restart  # or python3 main.py
```

See **[docs/README.md](docs/README.md)** for detailed instructions.

## Development

### Local Development

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env.example .env
nano .env  # Add your DISCORD_TOKEN

# Run bot
python3 main.py
```

### Docker Development

```bash
# Start bot
docker-compose up

# View logs
docker-compose logs -f bot

# Rebuild after changes
docker-compose up --build

# Stop bot
docker-compose down
```

See **[docs/DEVELOPMENT.MD](docs/DEVELOPMENT.MD)** for complete guide.

## Configuration

### Environment Variables

Create a `.env` file with:

```env
# Required
DISCORD_TOKEN=your_discord_bot_token_here

# Optional
LOG_LEVEL=INFO
LOG_LEVEL_COGS=INFO
DATABASE_PATH=task_manager.db
ICON_URL_FOOTER=https://your-icon-url.com/icon.png
```

### Cog Configuration

Each cog has a `config.json` file for customization:

```json
{
  "author_name": "Cog Name",
  "color": "0x3498DB",
  "log_level": "INFO",
  "database_module": "cog_db_functions"
}
```

## Currency System

The bot includes a shared currency system accessible by all cogs:

```python
import database

# Get balance
balance = database.get_balance(user_id, "tokens")

# Update balance
database.update_balance(user_id, "tokens", 100)

# Transfer currency
success = database.transfer_currency(sender_id, receiver_id, amount, "tokens")
```

See **[docs/DATABASE_ARCHITECTURE.md](docs/DATABASE_ARCHITECTURE.md)** for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally (both Python and Docker)
5. Submit a pull request

See **[DEVELOPMENT.MD](DEVELOPMENT.MD)** for guidelines.

## Troubleshooting

### Bot Won't Start

```bash
# Check token in .env
cat .env | grep DISCORD_TOKEN

# View logs
docker-compose logs bot  # Docker
# or check terminal output for local
```

### Commands Not Showing

- Wait a few minutes for Discord to sync
- Verify bot has `applications.commands` scope
- Check bot permissions in server

### Database Issues

```bash
# Reset database
rm task_manager.db
docker-compose up  # or python3 main.py
```

See **[docs/DEVELOPMENT.MD](docs/DEVELOPMENT.MD)** for more troubleshooting.

