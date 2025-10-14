import discord
from discord.ext import commands
import re

from cogs.base_cog import BaseCog
from cogs.stats import cog_db_functions as stats_db


class LinkFixer(BaseCog):
    """A cog to automatically fix social media links for better embeds."""
    __version__ = "1.0.0"

    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
    
    def default_config(self) -> dict:
        """Override default config with custom settings."""
        config = super().default_config()
        config["author_name"] = "Link Fixer"
        config["color"] = "0x1DA1F2"  # Twitter blue
        return config
    
    def _post_init(self):
        """Compile regex patterns for efficiency after base initialization."""
        # Compile regex patterns for efficiency
        self.twitter_pattern = re.compile(r"https?://(?:www\.)?twitter\.com/([a-zA-Z0-9_]+)(/status/\d+)?")
        self.x_pattern = re.compile(r"https?://(?:www\.)?x\.com/([a-zA-Z0-9_]+)(/status/\d+)?")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Listens for messages and fixes social media links."""
        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            return

        # Ignore messages in DMs
        if not message.guild:
            return

        original_content = message.content
        modified_content = self.twitter_pattern.sub(r"https://vxtwitter.com/\1\2", original_content)
        modified_content = self.x_pattern.sub(r"https://vxtwitter.com/\1\2", modified_content)

        # If the content was changed, send the new message and delete the old one
        if modified_content != original_content:
            self.logger.info(f"Fixing link in message from {message.author} in #{message.channel}")
            try:
                # Construct the new message content
                new_message = f'{message.author.mention} posted: {modified_content}'

                if message.reference and isinstance(message.reference.resolved, discord.Message):
                    # If the original message was a reply, reply to the same message
                    await message.reference.resolved.reply(new_message)
                else:
                    # Otherwise, just send to the channel
                    await message.channel.send(new_message)

                # Delete the original message
                await message.delete()
                
                # Track usage in stats
                stats_db.track_command_usage('fixtter')
                self.logger.debug("Tracked fixtter usage in stats")

            except discord.errors.Forbidden:
                self.logger.warning(f"Missing permissions to modify message in #{message.channel.name}")
            except Exception as e:
                self.logger.error(f"An error occurred while fixing a link: {e}", exc_info=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(LinkFixer(bot))

