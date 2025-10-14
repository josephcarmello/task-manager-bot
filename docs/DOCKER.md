# Docker Setup Guide

Complete guide for running the Task Manager Bot using Docker and Docker Compose.

---
Verify installation:
```bash
docker --version
docker-compose --version
```

---

## Quick Start

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd task-manager-bot

# 2. Copy environment template
cp env.example .env

# 3. Edit .env and add your Discord token
nano .env  # or use your preferred editor
# Add: DISCORD_TOKEN=your_token_here

# 4. Start the bot
docker-compose up

# That's it! Bot should now be online in Discord.
```

---

## Docker Commands

### Starting the Bot

```bash
# Start in foreground (see logs in terminal)
docker-compose up

# Start in background (detached mode)
docker-compose up -d

# Start with rebuild (after code changes)
docker-compose up --build
```

### Stopping the Bot

```bash
# Stop gracefully
docker-compose down

# Stop and remove volumes (resets database)
docker-compose down -v
```

### Viewing Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for specific service
docker-compose logs -f bot

# Last 100 lines
docker-compose logs --tail=100 bot
```

### Managing Containers

```bash
# List running containers
docker-compose ps

# Restart the bot
docker-compose restart

# Stop without removing containers
docker-compose stop

# Start stopped containers
docker-compose start
```

### Accessing the Container

```bash
# Open a shell in the running container
docker-compose exec bot bash

# Or use sh if bash is not available
docker-compose exec bot sh

# Run a command in the container
docker-compose exec bot python --version

# View environment variables
docker-compose exec bot env
```

---

## Development Workflow

### Making Code Changes

```bash
# 1. Edit your code locally
# 2. Rebuild and restart
docker-compose down
docker-compose up --build

# Quick one-liner
docker-compose down && docker-compose up --build
```

### Live Development (Hot Reload)

To enable live code reloading without rebuilding:

1. Uncomment the volume mounts in `docker-compose.yml`:

```yaml
volumes:
  - ./task_manager.db:/app/task_manager.db
  - ./cogs:/app/cogs:ro
  - ./database:/app/database:ro
  - ./main.py:/app/main.py:ro
```

2. Restart the container:

```bash
docker-compose down
docker-compose up
```

Now code changes will be reflected immediately (you'll still need to restart for Python changes to take effect).

### Testing Changes

```bash
# 1. Make your changes
# 2. Rebuild
docker-compose up --build

# 3. Check logs for errors
docker-compose logs -f bot

# 4. Test in Discord
# Use your bot commands in Discord

# 5. View logs for debugging
docker-compose logs --tail=50 bot
```

---

## File Structure with Docker

```
task-manager-bot/
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose configuration
├── env.example             # Environment template
├── .env                    # Your environment variables (create this)
├── .dockerignore           # Files to exclude from Docker build
├── task_manager.db         # Database (persisted via volume)
└── ... (rest of your code)
```

## Useful Docker Commands

```bash
# View Docker disk usage
docker system df

# Clean up unused containers/images
docker system prune

# View image history
docker history task-manager-bot

# Inspect container
docker inspect task-manager-bot

# View container resource usage
docker stats task-manager-bot

# Export container logs
docker-compose logs bot > bot.log

# Build without cache
docker-compose build --no-cache
```

---

## Summary

**Start bot:**
```bash
docker-compose up
```

**Stop bot:**
```bash
docker-compose down
```

**Rebuild after changes:**
```bash
docker-compose up --build
```

**View logs:**
```bash
docker-compose logs -f bot
```


