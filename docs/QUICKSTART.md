# Quick Start Guide

Get your Task Manager Bot up and running in under 5 minutes!

## Choose Your Setup Method

### 🐳 Method 1: Docker (Easiest)

**Prerequisites:** Docker Desktop installed

```bash
# 1. Clone
git clone <repo-url>
cd task-manager-bot

# 2. Setup environment
cp env.example .env
nano .env  # Add DISCORD_TOKEN=your_token_here

# 3. Start bot
docker-compose up

✅ Done! Bot is now online.
```

[Full Docker Documentation →](DOCKER.md)

---

### 🐍 Method 2: Local Python

**Prerequisites:** Python 3.11+ installed

```bash
# 1. Clone
git clone <repo-url>
cd task-manager-bot

# 2. Virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp env.example .env
nano .env  # Add DISCORD_TOKEN=your_token_here

# 5. Run bot
python3 main.py

✅ Done! Bot is now online.
```

[Full Development Documentation →](DEVELOPMENT.MD)

---

## Getting Your Discord Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create **New Application**
3. Go to **Bot** section → **Add Bot**
4. Click **Reset Token** and copy it
5. Paste into `.env` file: `DISCORD_TOKEN=your_token_here`

## Inviting Bot to Your Server

1. In Developer Portal, go to **OAuth2** → **URL Generator**
2. Select scopes: `bot`, `applications.commands`
3. Select permissions: Send Messages, Embed Links, Read Messages, Manage Messages
4. Copy generated URL and open in browser
5. Select your server and authorize

## Testing Your Bot

Once the bot is online, test these commands in Discord:

```
/info              # Bot information
/stats             # Usage statistics
/balance tokens    # Check token balance
```

Post a Twitter/X link to test the auto-fixer!

## Common Issues

**Bot offline?**
- Check logs for errors
- Verify DISCORD_TOKEN in `.env`
- Ensure bot has permissions

**Commands not showing?**
- Wait a few minutes for Discord to sync
- Check bot has `applications.commands` scope

**Need help?**
- Check [DEVELOPMENT.MD](DEVELOPMENT.MD) for detailed troubleshooting
- Review logs for error messages

---

## Next Steps

- **Add new commands**: See [Cogs README](README.md)
- **Customize bot**: Edit `config.json` files in each cog directory
- **Learn more**: Read [BASE_COG_GUIDE.md](BASE_COG_GUIDE.md)

---

## Documentation Index

| File | Purpose |
|------|---------|
| **QUICKSTART.md** | This file - get started fast |
| **DEVELOPMENT.MD** | Complete development guide |
| **DOCKER.md** | Docker-specific documentation |
| **DATABASE_ARCHITECTURE.md** | Database and currency system |
| **README.md** | Creating and managing cogs |
| **BASE_COG_GUIDE.md** | BaseCog usage guide |
| **QUICK_REFERENCE.md** | Command cheat sheet |

---

**Ready? Pick a method above and start coding!** 🚀

