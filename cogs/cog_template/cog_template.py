"""
Cog Template - A starting point for creating new cogs.

This template uses the BaseCog class to minimize boilerplate code.
To create a new cog:
1. Copy the cog_template folder and rename it
2. Rename this file to match your cog's name
3. Update the class name and commands
4. Update config.json with your cog's settings
"""

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from cogs.base_cog import BaseCog
import roles_config


class CogTemplate(BaseCog):
    """A template for creating new cogs."""
    
    # Set the version of your cog
    __version__ = "1.0.0"

    def __init__(self, bot: commands.Bot):
        # Initialize the base cog - handles config, logging, and DB setup
        super().__init__(bot)
    
    def default_config(self) -> dict:
        """
        Override this to provide custom default configuration.
        This is optional - only include if you want different defaults.
        """
        config = super().default_config()
        config["author_name"] = "My New Cog"
        config["color"] = "0x3498DB"  # Blue
        # You can add custom config keys here too
        config["my_custom_setting"] = "default_value"
        return config
    
    def _post_init(self):
        """
        Override this to do additional initialization after base setup.
        This is optional - only include if you need custom initialization.
        
        Called after config loading, logging setup, and DB module loading.
        """
        # Example: Initialize custom attributes
        # self.cache = {}
        # self.my_api_key = self.config.get("my_custom_setting")
        pass

    # --- EXAMPLE COMMANDS ---

    @app_commands.command(name="template-command", description="An example command for the template.")
    async def template_command(self, interaction: discord.Interaction):
        """This is a sample slash command."""
        self.logger.info(f"'template-command' used by {interaction.user.name}")

        # Example: Using the database module (if configured)
        if self.db:
            # Example: self.db.save_data(interaction.user.id, "some data")
            # Example: data = self.db.get_data(interaction.user.id)
            self.logger.debug("Database module is loaded and ready")
        else:
            self.logger.debug("Database module not loaded")

        # Use the inherited _create_embed method for consistent styling
        embed = self._create_embed(
            "Template Command", 
            "This is an example command from a cog.\n\nCheck out the code to see how easy it is!"
        )
        embed.add_field(
            name="Your User ID", 
            value=f"`{interaction.user.id}`", 
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="template-admin", description="[Admin Only] An example admin-only command.")
    @roles_config.has_role('admin')  # Restricts to users with 'admin' role
    async def template_admin(self, interaction: discord.Interaction):
        """This is a sample admin-only slash command."""
        self.logger.info(f"'template-admin' used by {interaction.user.name}")

        # Use helper method for success messages
        await self._send_success(
            interaction,
            "Admin Command",
            "You have admin permissions! 🎉"
        )

    @app_commands.command(name="template-save", description="Example command that uses the database.")
    @app_commands.describe(data="The data to save")
    async def template_save(self, interaction: discord.Interaction, data: str):
        """Example command showing database usage and error handling."""
        self.logger.info(f"'template-save' used by {interaction.user.name}")
        
        # Check if database module is configured
        if not self.db:
            await self._handle_db_error(interaction)
            return
        
        try:
            # Your database operations here
            # Example: self.db.save_user_data(interaction.user.id, data)
            
            # Use helper method for success messages
            await self._send_success(
                interaction,
                "Data Saved",
                f"Successfully saved: `{data}`"
            )
            
        except Exception as e:
            self.logger.error(f"Error saving data: {e}", exc_info=True)
            # Use helper method for error messages
            await self._send_error(
                interaction,
                "Save Failed",
                "An error occurred while saving your data."
            )

    @app_commands.command(name="template-info", description="Shows information about this cog.")
    async def template_info(self, interaction: discord.Interaction):
        """Display information about this cog."""
        embed = self._create_embed("Cog Information")
        
        embed.add_field(name="Version", value=f"`{self.__version__}`", inline=True)
        embed.add_field(name="Cog Name", value=f"`{self.cog_name}`", inline=True)
        embed.add_field(
            name="Database", 
            value="✅ Loaded" if self.db else "❌ Not Configured", 
            inline=True
        )
        
        # Show a custom config value (if you added one)
        custom_setting = self.config.get("my_custom_setting", "Not set")
        embed.add_field(
            name="Custom Setting", 
            value=f"`{custom_setting}`", 
            inline=False
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


# This function is REQUIRED for the bot to load the cog
async def setup(bot: commands.Bot):
    # Change 'CogTemplate' to the name of your class
    await bot.add_cog(CogTemplate(bot))

