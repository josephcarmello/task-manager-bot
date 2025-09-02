import discord
from discord import app_commands
from discord.ext import commands
import os
import logging
import json
import importlib
from typing import Optional

import roles_config
from logging_config import LOG_LEVELS

# Get the logger for this specific cog
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
        self.db = self._load_db_module()
        # This message will be logged when the cog is loaded successfully
        logger.info(f"CogTemplate v{self.__version__} loaded.")

    def _load_config(self):
        """Loads configuration from a JSON file in the same directory."""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            # Fallback for footer icon from environment variable if not in config
            self.config['footer_icon_url'] = self.config.get('footer_icon_url', os.getenv("ICON_URL_FOOTER"))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load config.json for CogTemplate: {e}", exc_info=True)
            # Default config if the file is missing or invalid
            self.config = {
                "author_name": "Default Cog",
                "author_icon_url": "",
                "footer_text": "Task Manager Bot",
                "footer_icon_url": os.getenv("ICON_URL_FOOTER", ""),
                "color": "0xCCCCCC", # Default grey color
                "database_module": None
            }

    def _load_db_module(self):
        """Dynamically loads the cog's database functions module if specified in the config."""
        db_module_name = self.config.get("database_module")
        if db_module_name:
            try:
                # IMPORTANT: The module path must match the cog's folder name
                module_path = f"cogs.cog_template.{db_module_name}"
                db_module = importlib.import_module(module_path)
                db_module.initialize_tables()
                logger.info(f"Successfully loaded and initialized database module: {module_path}")
                return db_module
            except ImportError as e:
                logger.error(f"Failed to load database module '{db_module_name}': {e}", exc_info=True)
        else:
            logger.debug("No database_module specified in config.json for CogTemplate.")
        return None

    def _setup_logging(self):
        """Sets the log level for this cog's logger."""
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
            text=self.config.get("footer_text", f"Task Manager Bot v{self.bot.version}"),
            icon_url=self.config.get("footer_icon_url", "")
        )
        return embed

    async def _handle_db_error(self, interaction: discord.Interaction):
        """Sends a generic error message if the DB module isn't loaded."""
        embed = self._create_embed("Command Error", "This command could not be processed because its database module is not configured correctly.")
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)

    #### --- EXAMPLE COMMANDS --- ###

    @app_commands.command(name="template-command", description="An example command for the template.")
    async def template_command(self, interaction: discord.Interaction):
        """This is a sample slash command."""
        logger.info(f"'template-command' used by {interaction.user.name}")

        # Example of how to use your cog-specific database functions
        if self.db:
            # e.g., self.db.save_my_data(interaction.user.id, "some data")
            pass
        else:
            # Optionally, handle the case where DB isn't configured for this command
            logger.debug("Database module not loaded for 'template-command', skipping DB operations.")


        embed = self._create_embed("Template Command", "This is an example command from a cog.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="template-admin", description="[Admin Only] An example admin-only command.")
    @roles_config.has_role('admin') # This decorator restricts the command to users with the 'admin' role
    async def template_admin(self, interaction: discord.Interaction):
        """This is a sample admin-only slash command."""
        logger.info(f"'template-admin' used by {interaction.user.name}")

        embed = self._create_embed("Admin Command", "You have the power!")
        await interaction.response.send_message(embed=embed, ephemeral=True)


# This function is required for the bot to load the cog
async def setup(bot: commands.Bot):
    # Change 'CogTemplate' to the name of your class
    await bot.add_cog(CogTemplate(bot))

