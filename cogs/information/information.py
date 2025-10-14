"""
Information Cog - Displays bot and system information.

This is a REFACTORED version demonstrating the use of BaseCog.
Compare this with information.py to see the code reduction!

To use this version:
1. Rename information.py to information_old.py
2. Rename this file to information.py
"""

import discord
from discord import app_commands
from discord.ext import commands
import platform

from cogs.base_cog import BaseCog
import roles_config


class Information(BaseCog):
    """A cog for displaying bot and system information."""
    __version__ = "1.0.0"

    def __init__(self, bot: commands.Bot):
        # That's it! All the boilerplate is handled by BaseCog
        super().__init__(bot)
    
    def default_config(self) -> dict:
        """Override default config with custom settings."""
        config = super().default_config()
        config["author_name"] = "Bot Information"
        config["color"] = "0x95A5A6"
        return config

    @app_commands.command(name="info", description="Displays detailed information about the bot.")
    async def info(self, interaction: discord.Interaction):
        """Shows bot version, Python version, and loaded cogs."""
        self.logger.info(f"'info' command used by {interaction.user.name}")

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
    @roles_config.has_role('admin')
    async def shutdown(self, interaction: discord.Interaction):
        """Shuts down the bot cleanly."""
        self.logger.warning(f"Shutdown command received from {interaction.user} (ID: {interaction.user.id})")
        embed = self._create_embed("Shutting Down", "The bot is now shutting down.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.bot.close()


async def setup(bot: commands.Bot):
    await bot.add_cog(Information(bot))

