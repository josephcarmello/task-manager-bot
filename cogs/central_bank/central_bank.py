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

class CentralBank(commands.Cog):
    """A cog for managing in-bot currency."""
    __version__ = "1.0.0"

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._load_config()
        self._setup_logging()
        logger.info(f"CentralBank Cog v{self.__version__} loaded.")

    def _load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
            self.config['footer_icon_url'] = self.config.get('footer_icon_url', os.getenv("ICON_URL_FOOTER"))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load config.json for CentralBank: {e}", exc_info=True)
            self.config = {
                "author_name": "Central Bank",
                "author_icon_url": "",
                "footer_text": "Task Manager Bot",
                "footer_icon_url": os.getenv("ICON_URL_FOOTER", ""),
                "color": "0x3498DB"
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
        logger.debug(f"CentralBank log level set to {log_level_str} (Source: {source})")

    @property
    def embed_color(self) -> int:
        return int(self.config.get('color', '0xCCCCCC'), 16)

    def _create_embed(self, title: str, description: str = "") -> discord.Embed:
        embed = discord.Embed(title=title, description=description, color=self.embed_color)
        embed.set_author(name=self.config["author_name"], icon_url=self.config["author_icon_url"])
        embed.set_footer(text=self.config["footer_text"], icon_url=self.config["footer_icon_url"])
        return embed

    @app_commands.command(name="balance", description="Check your balance for a specific currency.")
    @app_commands.describe(currency="The currency to check (e.g., tokens, credits).")
    async def balance(self, interaction: discord.Interaction, currency: str):
        database.track_command_usage('balance')
        user_id = interaction.user.id
        balance = database.get_balance(user_id, currency)
        embed = self._create_embed(
            f"{currency.title()} Balance",
            f"You have `{balance}` {currency}."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="pay", description="Pay another user in a specific currency.")
    @app_commands.describe(
        recipient="The user you want to pay.",
        amount="The amount of currency to send.",
        currency="The currency to send (e.g., tokens, credits)."
    )
    async def pay(self, interaction: discord.Interaction, recipient: discord.Member, amount: app_commands.Range[int, 1], currency: str):
        database.track_command_usage('pay')
        payer_id = interaction.user.id
        recipient_id = recipient.id

        if payer_id == recipient_id:
            embed = self._create_embed("Payment Error", "You cannot pay yourself.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        success = database.transfer_currency(payer_id, recipient_id, amount, currency)

        if success:
            embed = self._create_embed(
                "Payment Successful",
                f"You have successfully paid {recipient.mention} `{amount}` {currency}."
            )
            logger.info(f"'{interaction.user}' paid '{recipient}' {amount} {currency}.")
        else:
            embed = self._create_embed(
                "Payment Failed",
                f"You do not have enough {currency} to complete this transaction."
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="award", description="[Banker Only] Award currency to a user.")
    @app_commands.describe(
        recipient="The user to award currency to.",
        amount="The amount to award.",
        currency="The currency to award."
    )
    @has_role('banker')
    async def award(self, interaction: discord.Interaction, recipient: discord.Member, amount: int, currency: str):
        database.track_command_usage('award')
        recipient_id = recipient.id
        database.update_balance(recipient_id, currency, amount)

        embed = self._create_embed(
            "Currency Awarded",
            f"Successfully awarded `{amount}` {currency} to {recipient.mention}."
        )
        logger.info(
            f"'{interaction.user}' awarded {amount} {currency} to '{recipient}'."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(CentralBank(bot))
