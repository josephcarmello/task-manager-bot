import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv

from database import core as db_core
from logging_config import setup_logging

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

setup_logging()
logger = logging.getLogger(__name__)

# --- Task Manager - Bot Initialization!  ---

class TaskManagerBot(commands.Bot):
    """The main bot class for Task Manager."""
    __version__ = "1.0.0"

    def __init__(self):
        intents = discord.Intents.all()
        intents.members = True  # Required for some role/user operations
        super().__init__(command_prefix="!i@#@31@@!#", intents=intents)
        self.version = self.__version__ # Set the instance version attribute


    async def setup_hook(self):
        """This is called once the bot is ready to start its setup."""
        logger.info("Running setup_hook...")
        await self.load_all_cogs()
        await self.tree.sync()
        logger.info("Command tree synced.")

    async def load_all_cogs(self):
        """Scans the cogs directory for subdirectories and loads cogs from them."""
        logger.info("--- Loading Cogs ---")
        cogs_dir = 'cogs'
        for item in os.listdir(cogs_dir):
            path = os.path.join(cogs_dir, item)
            if os.path.isdir(path) and not item.startswith('__'):
                cog_name = item
                cog_path = f'cogs.{cog_name}.{cog_name}'
                try:
                    await self.load_extension(cog_path)
                    logger.info(f"Successfully loaded cog: {cog_name}")
                except Exception as e:
                    logger.error(f"Failed to load cog: {cog_name}", exc_info=e)
        logger.info("--- Cogs Loaded ---")

    async def on_ready(self):
        """Called when the bot is fully connected and ready."""
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info(f'Bot Version: {self.__version__}')
        logger.info('------')

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        logger.critical("DISCORD_TOKEN environment variable not set. Please create a .env file.")
    else:
        # Initialize the shared/core database tables before the bot starts
        db_core.initialize_database()
        bot = TaskManagerBot()
        bot.run(DISCORD_TOKEN)


