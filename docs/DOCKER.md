# Docker Setup Guide

Complete guide for running the Task Manager Bot using Docker and Docker Compose.

## Why Use Docker?

✅ **Consistent Environment** - Same setup on any machine  
✅ **Easy Setup** - No Python installation needed  
✅ **Isolated** - Doesn't affect your system  
✅ **Production-Ready** - Same setup for dev and production  

---

## Prerequisites

Install Docker Desktop for your operating system:

- **macOS**: [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
- **Windows**: [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
- **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)

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

### Docker Files Explained

**Dockerfile**
- Defines how to build the Docker image
- Installs Python dependencies
- Sets up the application environment
- Creates non-root user for security

**docker-compose.yml**
- Orchestrates the Docker container
- Loads environment variables from `.env`
- Mounts database volume for persistence
- Configures logging and restart policies

**env.example**
- Template for environment variables
- Copy to `.env` and fill in your values
- Never commit `.env` to version control

**.dockerignore**
- Excludes files from Docker build
- Reduces image size
- Prevents sensitive data from being copied

---

## Environment Variables

The bot uses environment variables from `.env` file.

### Required Variables

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

### Optional Variables

```env
LOG_LEVEL=INFO              # DEBUG, INFO, WARNING, ERROR
LOG_LEVEL_COGS=INFO         # Cog-specific log level
DATABASE_PATH=task_manager.db
ICON_URL_FOOTER=            # Footer icon URL
```

### Setting Up .env

```bash
# 1. Copy template
cp env.example .env

# 2. Edit with your values
nano .env

# 3. Ensure DISCORD_TOKEN is set
# DISCORD_TOKEN=your_actual_token_here

# 4. Save and restart bot
docker-compose down
docker-compose up
```

---

## Database Persistence

The SQLite database is persisted using Docker volumes.

### Database Location

```yaml
volumes:
  - ./task_manager.db:/app/task_manager.db
```

This mounts your local `task_manager.db` file into the container.

### Database Operations

**View database:**
```bash
# Install sqlite3 if not available
sqlite3 task_manager.db

# Run queries
.tables
SELECT * FROM users;
.exit
```

**Backup database:**
```bash
# Stop the bot
docker-compose down

# Backup database
cp task_manager.db task_manager.db.backup

# Restart bot
docker-compose up -d
```

**Reset database:**
```bash
# Stop the bot
docker-compose down

# Delete database
rm task_manager.db

# Restart bot (database will be recreated)
docker-compose up
```

**Restore from backup:**
```bash
docker-compose down
cp task_manager.db.backup task_manager.db
docker-compose up
```

---

## Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker-compose logs bot
```

**Common issues:**
- Missing `DISCORD_TOKEN` in `.env`
- Invalid Discord token
- Port conflicts
- Syntax errors in code

**Solution:**
```bash
# Verify .env exists and has token
cat .env | grep DISCORD_TOKEN

# Rebuild fresh
docker-compose down
docker-compose up --build
```

### Bot is Offline

**Check if container is running:**
```bash
docker-compose ps
```

**View logs:**
```bash
docker-compose logs -f bot
```

**Restart bot:**
```bash
docker-compose restart
```

### Changes Not Reflected

**Solution: Rebuild the image**
```bash
docker-compose down
docker-compose up --build --force-recreate
```

### Permission Errors

**Issue:** Database permission errors

**Solution:**
```bash
# On Linux, fix database permissions
chmod 666 task_manager.db

# Or run container as your user
docker-compose run --user $(id -u):$(id -g) bot
```

### Clean Slate

Remove everything and start fresh:

```bash
# Stop containers
docker-compose down

# Remove volumes (deletes database!)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Delete database file
rm task_manager.db

# Rebuild from scratch
docker-compose up --build
```

---

## Production Deployment

### Using Docker in Production

**Recommended changes for production:**

1. **Use environment variables instead of .env file:**
```bash
docker run -e DISCORD_TOKEN=$DISCORD_TOKEN task-manager-bot
```

2. **Set restart policy:**
```yaml
restart: always
```

3. **Add resource limits:**
```yaml
deploy:
  resources:
    limits:
      cpus: '0.5'
      memory: 512M
```

4. **Use Docker Compose in production:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

5. **Enable logging driver:**
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Health Checks

The Dockerfile includes a health check:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"
```

Check health status:
```bash
docker-compose ps
docker inspect --format='{{.State.Health.Status}}' task-manager-bot
```

---

## Advanced Configuration

### Multi-Stage Builds

For smaller images, use multi-stage builds:

```dockerfile
# Build stage
FROM python:3.13-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
CMD ["python", "-u", "main.py"]
```

### Docker Compose Override

Create `docker-compose.override.yml` for local development:

```yaml
version: '3.8'
services:
  bot:
    volumes:
      - ./cogs:/app/cogs:ro
      - ./database:/app/database:ro
    environment:
      - LOG_LEVEL=DEBUG
```

This file is automatically merged with `docker-compose.yml`.

### Networking

Connect to external services:

```yaml
services:
  bot:
    networks:
      - bot-network

networks:
  bot-network:
    driver: bridge
```

---

## Docker Best Practices

✅ **Keep images small** - Use slim base images  
✅ **Use .dockerignore** - Exclude unnecessary files  
✅ **Layer caching** - Copy requirements.txt before code  
✅ **Non-root user** - Run as unprivileged user  
✅ **Health checks** - Monitor container health  
✅ **Logging** - Configure proper log rotation  
✅ **Secrets** - Never hardcode tokens in images  

---

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

## Additional Resources

- **Docker Documentation**: https://docs.docker.com/
- **Docker Compose Docs**: https://docs.docker.com/compose/
- **Best Practices**: https://docs.docker.com/develop/dev-best-practices/
- **Security**: https://docs.docker.com/engine/security/

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

**That's all you need to know!** 🚀

For more details, see `DEVELOPMENT.MD`.

