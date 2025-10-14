import discord
from discord import app_commands
from discord.ext import commands

import roles_config
from cogs.base_cog import BaseCog
from database import core as db_core


class Stats(BaseCog):
    """A cog for tracking and displaying bot statistics."""
    __version__ = "1.1.0"

    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
    
    def default_config(self) -> dict:
        """Override default config with custom settings."""
        config = super().default_config()
        config["author_name"] = "Bot Statistics"
        config["color"] = "0xE67E22"
        config["database_module"] = "cog_db_functions"
        return config

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction, command: app_commands.Command):
        """Listens for any successful slash command invocation and tracks it."""
        if self.db:
            try:
                self.db.track_command_usage(command.name)
                self.logger.debug(f"Tracked usage for command: /{command.name}")
            except Exception as e:
                self.logger.error(f"Failed to track command usage for '{command.name}': {e}", exc_info=True)
        else:
            self.logger.warning("Stats DB module not loaded, skipping command usage tracking.")

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
            self.logger.error(f"Error in 'stats' command: {e}", exc_info=True)
            await self._send_error(interaction, "Error", "Could not retrieve bot statistics.")

    @app_commands.command(name="reset-stats", description="[Admin Only] Resets all command usage statistics.")
    @roles_config.has_role('admin')
    async def reset_stats(self, interaction: discord.Interaction):
        """Resets the command usage counters in the database."""
        if not self.db:
            await self._handle_db_error(interaction)
            return

        try:
            self.db.reset_all_command_usage()
            self.logger.warning(f"Command stats reset by {interaction.user} (ID: {interaction.user.id})")
            await self._send_success(interaction, "Statistics Reset", "All command usage statistics have been reset to zero.")
        except Exception as e:
            self.logger.error(f"Error in 'reset-stats' command: {e}", exc_info=True)
            await self._send_error(interaction, "Error", "An error occurred while resetting statistics.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Stats(bot))

