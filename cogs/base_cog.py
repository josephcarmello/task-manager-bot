"""
Base Cog Class - Provides common functionality for all cogs.

This module contains the BaseCog class which handles:
- Configuration loading from config.json
- Logging setup
- Database module loading (optional)
- Standardized embed creation
- Common error handling

All cogs should inherit from BaseCog to reduce code duplication.
"""

import discord
from discord.ext import commands
import os
import logging
import json
import importlib
from typing import Optional

from logging_config import LOG_LEVELS


class BaseCog(commands.Cog):
    """
    Base class for all cogs in the Task Manager Bot.
    
    Provides common functionality:
    - Automatic config loading from config.json in the cog's directory
    - Logging setup with configurable log levels
    - Optional database module loading
    - Standardized Discord embed creation
    - Error handling helpers
    
    To use:
    1. Inherit from BaseCog instead of commands.Cog
    2. Set __version__ in your class
    3. Call super().__init__(bot, cog_name) in your __init__
    4. Override default_config() if you need custom default configuration
    5. Override _post_init() if you need additional initialization after base setup
    """
    
    __version__ = "1.0.0"  # Override this in child classes
    
    def __init__(self, bot: commands.Bot, cog_name: str = None):
        """
        Initialize the base cog.
        
        Args:
            bot: The Discord bot instance
            cog_name: Name of the cog (auto-detected if not provided)
        """
        self.bot = bot
        
        # Auto-detect cog name from module path (directory name)
        if cog_name:
            self.cog_name = cog_name
        else:
            # Extract cog name from module path (e.g., 'cogs.central_bank.central_bank' -> 'central_bank')
            module_parts = self.__class__.__module__.split('.')
            if len(module_parts) >= 2:
                self.cog_name = module_parts[1]  # Get the directory name
            else:
                self.cog_name = self.__class__.__name__
        
        # Set up logger for this cog
        self.logger = logging.getLogger(f"cogs.{self.cog_name}")
        
        # Load configuration and setup
        self.config = self._load_config()
        self._setup_logging()
        self.db = self._load_db_module()
        
        # Call post-initialization hook for child classes
        self._post_init()
        
        self.logger.info(f"{self.cog_name} Cog v{self.__version__} loaded.")
    
    def _post_init(self):
        """
        Hook for child classes to perform additional initialization.
        Override this method if you need to do additional setup after base initialization.
        """
        pass
    
    def default_config(self) -> dict:
        """
        Returns the default configuration for this cog.
        Override this method in child classes to provide custom defaults.
        
        Returns:
            dict: Default configuration values
        """
        return {
            "author_name": f"{self.cog_name}",
            "author_icon_url": "",
            "footer_text": "Task Manager Bot",
            "footer_icon_url": os.getenv("ICON_URL_FOOTER", ""),
            "color": "0xCCCCCC",  # Default grey
            "log_level": "INFO",
            "database_module": None
        }
    
    def _load_config(self) -> dict:
        """
        Loads configuration from config.json in the cog's directory.
        Falls back to default_config() if file is missing or invalid.
        
        Returns:
            dict: Configuration dictionary
        """
        # Determine the config path based on the cog's file location
        cog_file = os.path.abspath(self.__class__.__module__.replace('.', os.sep) + '.py')
        cog_dir = os.path.dirname(cog_file)
        config_path = os.path.join(cog_dir, 'config.json')
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Merge with defaults for any missing keys
            default = self.default_config()
            for key, value in default.items():
                if key not in config:
                    config[key] = value
            
            # Fallback for footer icon from environment variable
            config['footer_icon_url'] = config.get('footer_icon_url', os.getenv("ICON_URL_FOOTER", ""))
            
            return config
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            if self.logger:
                self.logger.error(f"Failed to load config.json for {self.cog_name}: {e}", exc_info=True)
            return self.default_config()
    
    def _setup_logging(self):
        """Sets the log level for this cog's logger from config or environment."""
        log_level_str = self.config.get("log_level")
        source = "config.json"
        
        if not log_level_str:
            log_level_str = os.getenv("LOG_LEVEL_COGS", "INFO")
            source = "env/default"
        
        log_level_str = log_level_str.upper()
        log_level = LOG_LEVELS.get(log_level_str, logging.INFO)
        self.logger.setLevel(log_level)
        self.logger.debug(f"{self.cog_name} log level set to {log_level_str} (Source: {source})")
    
    def _load_db_module(self) -> Optional[object]:
        """
        Dynamically loads the cog's database module if specified in config.
        The module should have an initialize_tables() function.
        
        Returns:
            The loaded database module or None if not configured
        """
        db_module_name = self.config.get("database_module")
        if db_module_name:
            try:
                # Construct module path based on cog name (already includes proper directory name)
                module_path = f"cogs.{self.cog_name}.{db_module_name}"
                db_module = importlib.import_module(module_path)
                
                # Initialize tables if the function exists
                if hasattr(db_module, 'initialize_tables'):
                    db_module.initialize_tables()
                    self.logger.info(f"Successfully loaded and initialized database module: {module_path}")
                else:
                    self.logger.warning(f"Database module '{module_path}' has no initialize_tables() function")
                
                return db_module
                
            except ImportError as e:
                self.logger.error(f"Failed to load database module '{db_module_name}': {e}", exc_info=True)
        else:
            self.logger.debug(f"No database_module specified in config.json for {self.cog_name}.")
        
        return None
    
    @property
    def embed_color(self) -> int:
        """
        Returns the color for embeds as an integer.
        
        Returns:
            int: Hex color value as integer
        """
        return int(self.config.get('color', '0xCCCCCC'), 16)
    
    def _create_embed(self, title: str, description: str = "") -> discord.Embed:
        """
        Creates a standardized Discord embed for this cog.
        
        Args:
            title: The embed title
            description: The embed description (optional)
        
        Returns:
            discord.Embed: Configured embed object
        """
        embed = discord.Embed(
            title=title,
            description=description,
            color=self.embed_color
        )
        embed.set_author(
            name=self.config.get("author_name", self.cog_name),
            icon_url=self.config.get("author_icon_url", "")
        )
        embed.set_footer(
            text=self.config.get("footer_text", f"Task Manager Bot v{self.bot.version}"),
            icon_url=self.config.get("footer_icon_url", "")
        )
        return embed
    
    async def _handle_db_error(self, interaction: discord.Interaction, custom_message: str = None):
        """
        Sends a generic error message if the DB module isn't loaded.
        
        Args:
            interaction: The Discord interaction
            custom_message: Optional custom error message
        """
        message = custom_message or "This command could not be processed because its database module is not configured correctly."
        embed = self._create_embed("Command Error", message)
        
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def _send_error(self, interaction: discord.Interaction, title: str, message: str, ephemeral: bool = True):
        """
        Helper to send error embeds to users.
        
        Args:
            interaction: The Discord interaction
            title: Error title
            message: Error message
            ephemeral: Whether the message should be ephemeral
        """
        embed = self._create_embed(title, message)
        
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
    
    async def _send_success(self, interaction: discord.Interaction, title: str, message: str, ephemeral: bool = True):
        """
        Helper to send success embeds to users.
        
        Args:
            interaction: The Discord interaction
            title: Success title
            message: Success message
            ephemeral: Whether the message should be ephemeral
        """
        embed = self._create_embed(title, message)
        
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=ephemeral)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

