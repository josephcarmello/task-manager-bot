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
from database import core as db_core

logger = logging.getLogger(__name__)

class Stats(commands.Cog):
    """A cog for tracking and displaying bot statistics."""
    __version__ = "1.1.0"

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._load_config()
        self._setup_logging()
        self.db = self._load_db_module()
        logger.info(f"Stats Cog v{self.__version__} loaded.")

    def _load_config(self):
        """Loads configuration from a JSON file in the same directory."""
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            self.config['footer_icon_url'] = self.config.get('footer_icon_url', os.getenv("ICON_URL_FOOTER"))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load config.json for Stats: {e}", exc_info=True)
            self.config = {
                "author_name": "Bot Statistics",
                "author_icon_url": "",
                "footer_text": "Task Manager Bot",
                "footer_icon_url": os.getenv("ICON_URL_FOOTER", ""),
                "color": "0xE67E22",
                "database_module": None
            }

    def _load_db_module(self):
        """Dynamically loads the cog's database functions module if specified in the config."""
        db_module_name = self.config.get("database_module")
        if db_module_name:
            try:
                module_path = f"cogs.stats.{db_module_name}"
                db_module = importlib.import_module(module_path)
                db_module.initialize_tables()
                logger.info(f"Successfully loaded and initialized database module: {module_path}")
                return db_module
            except ImportError as e:
                logger.error(f"Failed to load database module '{db_module_name}': {e}", exc_info=True)
        else:
            logger.debug("No database_module specified in config.json for Stats.")
        return None

    def _setup_logging(self):
        """Sets the log level for this cog's logger."""
        log_level_str = self.config.get("log_level")
        source = "config.json"
        if not log_level_str:
            log_level_str = os.getenv("LOG_LEVEL_COGS", "INFO")
            source = "env/default"
        log_level_str = log_level_str.upper()
        log_level = LOG_LEVELS.get(log_level_str, logging.INFO)
        logger.setLevel(log_level)
        logger.debug(f"Stats log level set to {log_level_str} (Source: {source})")

    @property
    def embed_color(self) -> int:
        """Returns the color for embeds as an integer."""
        return int(self.config.get('color', '0xCCCCCC'), 16)

    def _create_embed(self, title: str, description: str = "") -> discord.Embed:
        """A helper function to create standardized embeds for this cog."""
        embed = discord.Embed(title=title, description=description, color=self.embed_color)
        embed.set_author(name=self.config["author_name"], icon_url=self.config.get("author_icon_url", ""))
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

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction, command: app_commands.Command):
        """Listens for any successful slash command invocation and tracks it."""
        if self.db:
            try:
                self.db.track_command_usage(command.name)
                logger.debug(f"Tracked usage for command: /{command.name}")
            except Exception as e:
                logger.error(f"Failed to track command usage for '{command.name}': {e}", exc_info=True)
        else:
            logger.warning("Stats DB module not loaded, skipping command usage tracking.")

    @app_commands.command(name="stats", description="Displays usage statistics for the bot.")
    async def stats(self, interaction: discord.Interaction):
        """Shows command usage stats and total users."""
        if not self.db:
            await self._handle_db_error(interaction)
            return

        try:
            total_users = db_core.get_total_users()
            command_counts = self.db.get_all_command_usage()

            embed = self._create_embed("Bot Usage Statistics")
            embed.add_field(name="Total Unique Users", value=f"`{total_users}`", inline=False)

            if command_counts:
                # Sort by count descending, then by name ascending
                sorted_commands = sorted(command_counts.items(), key=lambda item: (-item[1], item[0]))
                value_str = "\n".join([f"`/{cmd}`: {count}" for cmd, count in sorted_commands])
                embed.add_field(name="Command Usage", value=value_str, inline=False)
            else:
                embed.add_field(name="Command Usage", value="No commands have been used yet.", inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in 'stats' command: {e}", exc_info=True)
            embed = self._create_embed("Error", "Could not retrieve bot statistics.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="reset-stats", description="[Admin Only] Resets all command usage statistics.")
    @roles_config.has_role('admin')
    async def reset_stats(self, interaction: discord.Interaction):
        """Resets the command usage counters in the database."""
        if not self.db:
            await self._handle_db_error(interaction)
            return

        try:
            self.db.reset_all_command_usage()
            logger.warning(f"Command stats reset by {interaction.user} (ID: {interaction.user.id})")
            embed = self._create_embed("Statistics Reset", "All command usage statistics have been reset to zero.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in 'reset-stats' command: {e}", exc_info=True)
            embed = self._create_embed("Error", "An error occurred while resetting statistics.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Stats(bot))


