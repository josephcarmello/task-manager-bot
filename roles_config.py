import discord
from discord import app_commands
import os
import logging


logger = logging.getLogger(__name__)

# This dictionary maps a friendly role name to the .env variable that should hold the role's ID.
# To add a new role, just add a new entry here and in your .env file.
ROLE_MAPPING = {
    'admin': 'ROLE_ID_ADMIN',
    'mod': 'ROLE_ID_MOD',
    'special': 'ROLE_ID_SPECIAL',
    'banker': 'ROLE_ID_BANKER',
}

def get_role_id(role_name: str) -> int | None:
    """
    Gets a role ID from environment variables based on its friendly name.
    Returns the integer ID if found and valid, otherwise None.
    """
    env_var = ROLE_MAPPING.get(role_name.lower())
    if not env_var:
        return None

    role_id_str = os.getenv(env_var)
    if role_id_str and role_id_str.isdigit():
        return int(role_id_str)

    logger.warning(
        f"Role ID for '{role_name}' ({env_var}) is not defined or invalid in the .env file."
    )
    return None

def has_role(required_role: str):
    """
    A decorator that checks if the user invoking a command has a specific role.

    This is designed to be used with `app_commands`. It checks the user's roles
    against an ID configured in the .env file.

    Args:
        required_role (str): The friendly name of the role to check (e.g., 'admin', 'banker').
    """
    async def predicate(interaction: discord.Interaction) -> bool:
        """The actual check that is executed by discord.py."""
        # Get the required role ID from .env using our helper
        role_id = get_role_id(required_role)

        # Safety check: If the role isn't configured in .env, deny access.
        if not role_id:
            await interaction.response.send_message(
                "This command is not configured correctly by the bot owner. Please contact an admin.",
                ephemeral=True
            )
            return False

        # Check if any of the user's roles match the required ID
        if any(role.id == role_id for role in interaction.user.roles):
            return True
        else:
            # The user does not have the role. Send a clear message and block the command.
            await interaction.response.send_message(
                f"You do not have the required permissions (`{required_role.capitalize()}`) to use this command.",
                ephemeral=True
            )
            return False

    return app_commands.check(predicate)


