import discord
from discord import app_commands
from discord.ext import commands
import os
import logging
import json
from typing import Optional

import database
from roles_config import has_role
from logging_config import LOG_LEVELS

# Get the logger for this specific cog
# The logger is configured in the main bot file (main.py)
logger = logging.getLogger(__name__)

# Change the class name to reflect your cog's purpose
class CogTemplate(commands.Cog):
    """A template for creating new cogs."""

    # Set the version of your cog
    __version__ = "1.0.0"

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._load_config()
        self._setup_logging()
        # This message will be logged when the cog is loaded successfully
        logger.info(f"CogTemplate v{self.__version__} loaded.")

    def _load_config(self):
        """Loads configuration from a JSON file in the same directory."""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            # Fallback for footer icon from environment variable if not in config
            self.config['footer_icon_url'] = self.config.get('footer_icon_url', os.getenv("ICON_URL_FOOTer"))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load config.json for CogTemplate: {e}", exc_info=True)
            # Default config if the file is missing or invalid
            self.config = {
                "author_name": "Default Cog",
                "author_icon_url": "",
                "footer_text": "Task Manager Bot",
                "footer_icon_url": os.getenv("ICON_URL_FOOTER", ""),
                "color": "0xCCCCCC" # Default grey color
            }

    def _setup_logging(self):
        """Sets the log level for this cog's logger."""
        # Check for a log level in the cog's config, otherwise fall back to the global setting
        log_level_str = self.config.get("log_level")
        source = "config.json"
        if not log_level_str:
            log_level_str = os.getenv("LOG_LEVEL_COGS", "INFO") # Fallback to .env variable
            source = "env/default"

        log_level_str = log_level_str.upper()
        log_level = LOG_LEVELS.get(log_level_str, logging.INFO)
        logger.setLevel(log_level)
        logger.debug(f"CogTemplate log level set to {log_level_str} (Source: {source})")

    @property
    def embed_color(self) -> int:
        """Returns the color for embeds as an integer."""
        return int(self.config.get('color', '0xCCCCCC'), 16)

    def _create_embed(self, title: str, description: str = "") -> discord.Embed:
        """A helper function to create standardized embeds for this cog."""
        embed = discord.Embed(
            title=title,
            description=description,
            color=self.embed_color
        )
        embed.set_author(
            name=self.config["author_name"],
            icon_url=self.config["author_icon_url"]
        )
        embed.set_footer(
            text=self.config["footer_text"],
            icon_url=self.config["footer_icon_url"]
        )
        return embed

    #### --- EXAMPLE COMMANDS --- ###

    @app_commands.command(name="template-command", description="An example command for the template.")
    async def template_command(self, interaction: discord.Interaction):
        """This is a sample slash command."""
        # Always track command usage for statistics
        database.track_command_usage('template-command')

        logger.info(f"'template-command' used by {interaction.user.name}")

        embed = self._create_embed("Template Command", "This is an example command from a cog.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="template-admin", description="[Admin Only] An example admin-only command.")
    @has_role('admin') # This decorator restricts the command to users with the 'admin' role
    async def template_admin(self, interaction: discord.Interaction):
        """This is a sample admin-only slash command."""
        database.track_command_usage('template-admin')

        logger.info(f"'template-admin' used by {interaction.user.name}")

        embed = self._create_embed("Admin Command", "You have the power!")
        await interaction.response.send_message(embed=embed, ephemeral=True)


# This function is required for the bot to load the cog
async def setup(bot: commands.Bot):
    # Change 'CogTemplate' to the name of your class
    await bot.add_cog(CogTemplate(bot))



