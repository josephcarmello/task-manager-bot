import discord
from discord import app_commands
from discord.ext import commands

import database
from roles_config import has_role
from cogs.base_cog import BaseCog


class CentralBank(BaseCog):
    """A cog for managing in-bot currency."""
    __version__ = "1.0.0"

    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
    
    def default_config(self) -> dict:
        """Override default config with custom settings."""
        config = super().default_config()
        config["author_name"] = "Central Bank"
        config["color"] = "0x3498DB"
        return config

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
            await self._send_error(interaction, "Payment Error", "You cannot pay yourself.")
            return

        success = database.transfer_currency(payer_id, recipient_id, amount, currency)

        if success:
            embed = self._create_embed(
                "Payment Successful",
                f"You have successfully paid {recipient.mention} `{amount}` {currency}."
            )
            self.logger.info(f"'{interaction.user}' paid '{recipient}' {amount} {currency}.")
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
        self.logger.info(
            f"'{interaction.user}' awarded {amount} {currency} to '{recipient}'."
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(CentralBank(bot))

