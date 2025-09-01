import discord
from discord import app_commands
from discord.ext import commands
import os
import platform
import logging
import json

import database
from roles_config import has_role
from logging_config import LOG_LEVELS

logger = logging.getLogger(__name__)

class Information(commands.Cog):
    """A cog for displaying bot and system information."""
    __version__ = "1.0.0"

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._load_config()
        self._setup_logging()
        logger.info(f"Information Cog v{self.__version__} loaded.")

    def _load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            self.config['footer_icon_url'] = self.config.get('footer_icon_url', os.getenv("ICON_URL_FOOTER"))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load config.json for Information: {e}", exc_info=True)
            self.config = {
                "author_name": "Bot Information", "author_icon_url": "",
                "footer_text": "Task Manager Bot", "footer_icon_url": os.getenv("ICON_URL_FOOTER", ""),
                "color": "0x95A5A6"
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
        logger.debug(f"Information log level set to {log_level_str} (Source: {source})")

    @property
    def embed_color(self) -> int:
        return int(self.config.get('color', '0xCCCCCC'), 16)

    def _create_embed(self, title: str, description: str = "") -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=self.embed_color)
        embed.set_author(name=self.config["author_name"], icon_url=self.config["author_icon_url"])
        embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
        return embed

    @app_commands.command(name="info", description="Displays detailed information about the bot.")
    async def info(self, interaction: discord.Interaction):
        """Shows bot version, Python version, and loaded cogs."""
        database.track_command_usage('info')

        embed = self._create_embed("Bot Information")

        # Bot and system info
        embed.add_field(name="Bot Version", value=f"`{self.bot.version}`", inline=True)
        embed.add_field(name="Python Version", value=f"`{platform.python_version()}`", inline=True)
        embed.add_field(name="discord.py Version", value=f"`{discord.__version__}`", inline=True)

        # Cogs info
        loaded_cogs = []
        for cog_name, cog_instance in self.bot.cogs.items():
            version = getattr(cog_instance, '__version__', 'N/A')
            loaded_cogs.append(f"`{cog_name}` (v{version})")

        if loaded_cogs:
            embed.add_field(name="Loaded Cogs", value="\n".join(loaded_cogs), inline=False)
        else:
            embed.add_field(name="Loaded Cogs", value="No cogs are currently loaded.", inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="shutdown", description="[Admin Only] Shuts down the bot.")
    @has_role('admin')
    async def shutdown(self, interaction: discord.Interaction):
        """Shuts down the bot cleanly."""
        logger.warning(f"Shutdown command received from {interaction.user} (ID: {interaction.user.id})")
        embed = self._create_embed("Shutting Down", "The bot is now shutting down.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.bot.close()

async def setup(bot: commands.Bot):
    await bot.add_cog(Information(bot))



