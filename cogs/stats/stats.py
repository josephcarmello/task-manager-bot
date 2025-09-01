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

logger = logging.getLogger(__name__)

class Stats(commands.Cog):
    """A cog for tracking and displaying bot statistics."""
    __version__ = "1.0.0"

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._load_config()
        self._setup_logging()
        logger.info(f"Stats Cog v{self.__version__} loaded.")

    def _load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            self.config['footer_icon_url'] = self.config.get('footer_icon_url', os.getenv("ICON_URL_FOOTER"))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load config.json for Stats: {e}", exc_info=True)
            self.config = {
                "author_name": "Bot Statistics", "author_icon_url": "",
                "footer_text": "Task Manager Bot", "footer_icon_url": os.getenv("ICON_URL_FOOTER", ""),
                "color": "0xE67E22"
            }

    def _setup_logging(self):
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
        return int(self.config.get('color', '0xCCCCCC'), 16)

    def _create_embed(self, title: str, description: str = "") -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=self.embed_color)
        embed.set_author(name=self.config["author_name"], icon_url=self.config["author_icon_url"])
        embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
        return embed

    @app_commands.command(name="stats", description="Displays usage statistics for the bot.")
    async def stats(self, interaction: discord.Interaction):
        """Shows command usage stats and total users."""
        database.track_command_usage('stats')

        try:
            total_users = database.get_total_users()
            command_counts = database.get_all_command_usage()

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
    @has_role('admin')
    async def reset_stats(self, interaction: discord.Interaction):
        """Resets the command usage counters in the database."""
        try:
            database.reset_all_command_usage()
            logger.warning(f"Command stats reset by {interaction.user} (ID: {interaction.user.id})")
            embed = self._create_embed("Statistics Reset", "All command usage statistics have been reset to zero.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Error in 'reset-stats' command: {e}", exc_info=True)
            embed = self._create_embed("Error", "An error occurred while resetting statistics.")
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Stats(bot))
