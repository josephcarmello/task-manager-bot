"""
Translate Cog - Translates text between different languages.

This cog provides translation functionality using Google Translate API.
Users can specify both source and destination languages, or let the bot
auto-detect the source language. Weeeeeee.
"""

import discord
from discord import app_commands
from discord.ext import commands
from deep_translator import GoogleTranslator
import logging

from cogs.base_cog import BaseCog

# Language mapping for deep-translator (uses language names, not codes)
# Common languages with their codes and names
LANGUAGE_MAP = {
    'af': 'afrikaans', 'sq': 'albanian', 'am': 'amharic', 'ar': 'arabic', 'hy': 'armenian',
    'az': 'azerbaijani', 'eu': 'basque', 'be': 'belarusian', 'bn': 'bengali', 'bs': 'bosnian',
    'bg': 'bulgarian', 'ca': 'catalan', 'ceb': 'cebuano', 'ny': 'chichewa', 'zh-cn': 'chinese (simplified)',
    'zh-tw': 'chinese (traditional)', 'co': 'corsican', 'hr': 'croatian', 'cs': 'czech', 'da': 'danish',
    'nl': 'dutch', 'en': 'english', 'eo': 'esperanto', 'et': 'estonian', 'tl': 'filipino',
    'fi': 'finnish', 'fr': 'french', 'fy': 'frisian', 'gl': 'galician', 'ka': 'georgian',
    'de': 'german', 'el': 'greek', 'gu': 'gujarati', 'ht': 'haitian creole', 'ha': 'hausa',
    'haw': 'hawaiian', 'iw': 'hebrew', 'he': 'hebrew', 'hi': 'hindi', 'hmn': 'hmong',
    'hu': 'hungarian', 'is': 'icelandic', 'ig': 'igbo', 'id': 'indonesian', 'ga': 'irish',
    'it': 'italian', 'ja': 'japanese', 'jw': 'javanese', 'kn': 'kannada', 'kk': 'kazakh',
    'km': 'khmer', 'ko': 'korean', 'ku': 'kurdish (kurmanji)', 'ky': 'kyrgyz', 'lo': 'lao',
    'la': 'latin', 'lv': 'latvian', 'lt': 'lithuanian', 'lb': 'luxembourgish', 'mk': 'macedonian',
    'mg': 'malagasy', 'ms': 'malay', 'ml': 'malayalam', 'mt': 'maltese', 'mi': 'maori',
    'mr': 'marathi', 'mn': 'mongolian', 'my': 'myanmar (burmese)', 'ne': 'nepali', 'no': 'norwegian',
    'ps': 'pashto', 'fa': 'persian', 'pl': 'polish', 'pt': 'portuguese', 'pa': 'punjabi',
    'ro': 'romanian', 'ru': 'russian', 'sm': 'samoan', 'gd': 'scots gaelic', 'sr': 'serbian',
    'st': 'sesotho', 'sn': 'shona', 'sd': 'sindhi', 'si': 'sinhala', 'sk': 'slovak',
    'sl': 'slovenian', 'so': 'somali', 'es': 'spanish', 'su': 'sundanese', 'sw': 'swahili',
    'sv': 'swedish', 'tg': 'tajik', 'ta': 'tamil', 'tt': 'tatar', 'te': 'telugu',
    'th': 'thai', 'tr': 'turkish', 'uk': 'ukrainian', 'ur': 'urdu', 'ug': 'uyghur',
    'uz': 'uzbek', 'vi': 'vietnamese', 'cy': 'welsh', 'xh': 'xhosa', 'yi': 'yiddish',
    'yo': 'yoruba', 'zu': 'zulu', 'auto': 'auto'
}

# Reverse mapping for display names
LANGUAGE_DISPLAY_NAMES = {
    'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic', 'hy': 'Armenian',
    'az': 'Azerbaijani', 'eu': 'Basque', 'be': 'Belarusian', 'bn': 'Bengali', 'bs': 'Bosnian',
    'bg': 'Bulgarian', 'ca': 'Catalan', 'ceb': 'Cebuano', 'ny': 'Chichewa', 'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)', 'co': 'Corsican', 'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish',
    'nl': 'Dutch', 'en': 'English', 'eo': 'Esperanto', 'et': 'Estonian', 'tl': 'Filipino',
    'fi': 'Finnish', 'fr': 'French', 'fy': 'Frisian', 'gl': 'Galician', 'ka': 'Georgian',
    'de': 'German', 'el': 'Greek', 'gu': 'Gujarati', 'ht': 'Haitian Creole', 'ha': 'Hausa',
    'haw': 'Hawaiian', 'iw': 'Hebrew', 'he': 'Hebrew', 'hi': 'Hindi', 'hmn': 'Hmong',
    'hu': 'Hungarian', 'is': 'Icelandic', 'ig': 'Igbo', 'id': 'Indonesian', 'ga': 'Irish',
    'it': 'Italian', 'ja': 'Japanese', 'jw': 'Javanese', 'kn': 'Kannada', 'kk': 'Kazakh',
    'km': 'Khmer', 'ko': 'Korean', 'ku': 'Kurdish (Kurmanji)', 'ky': 'Kyrgyz', 'lo': 'Lao',
    'la': 'Latin', 'lv': 'Latvian', 'lt': 'Lithuanian', 'lb': 'Luxembourgish', 'mk': 'Macedonian',
    'mg': 'Malagasy', 'ms': 'Malay', 'ml': 'Malayalam', 'mt': 'Maltese', 'mi': 'Maori',
    'mr': 'Marathi', 'mn': 'Mongolian', 'my': 'Myanmar (Burmese)', 'ne': 'Nepali', 'no': 'Norwegian',
    'ps': 'Pashto', 'fa': 'Persian', 'pl': 'Polish', 'pt': 'Portuguese', 'pa': 'Punjabi',
    'ro': 'Romanian', 'ru': 'Russian', 'sm': 'Samoan', 'gd': 'Scots Gaelic', 'sr': 'Serbian',
    'st': 'Sesotho', 'sn': 'Shona', 'sd': 'Sindhi', 'si': 'Sinhala', 'sk': 'Slovak',
    'sl': 'Slovenian', 'so': 'Somali', 'es': 'Spanish', 'su': 'Sundanese', 'sw': 'Swahili',
    'sv': 'Swedish', 'tg': 'Tajik', 'ta': 'Tamil', 'tt': 'Tatar', 'te': 'Telugu',
    'th': 'Thai', 'tr': 'Turkish', 'uk': 'Ukrainian', 'ur': 'Urdu', 'ug': 'Uyghur',
    'uz': 'Uzbek', 'vi': 'Vietnamese', 'cy': 'Welsh', 'xh': 'Xhosa', 'yi': 'Yiddish',
    'yo': 'Yoruba', 'zu': 'Zulu', 'auto': 'Auto-detect'
}


class Translate(BaseCog):
    """A cog for translating text between languages."""
    __version__ = "1.0.0"

    def __init__(self, bot: commands.Bot):
        super().__init__(bot)
        self.language_choices = [
            app_commands.Choice(name=f"{LANGUAGE_DISPLAY_NAMES.get(code, code)} ({code})", value=code)
            for code in sorted(LANGUAGE_DISPLAY_NAMES.keys(), key=lambda x: LANGUAGE_DISPLAY_NAMES.get(x, x))
            if code != 'auto'  # Exclude auto from destination choices...
        ]

    def default_config(self) -> dict:
        """Override default config with custom settings."""
        config = super().default_config()
        config["author_name"] = "Translation Service"
        config["color"] = "0x3498DB"
        return config

    async def language_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        """Autocomplete function for language selection."""
        if not current:
            return self.language_choices[:25]  # Discord limit is 25 choices- fun times.
        
        current_lower = current.lower()
        filtered = [
            choice for choice in self.language_choices
            if current_lower in choice.name.lower() or current_lower in choice.value.lower()
        ]
        return filtered[:25]

    @app_commands.command(name="translate", description="Translate text from one language to another")
    @app_commands.describe(
        text="The text you want to translate",
        to_language="The language to translate to",
        from_language="The source language (leave empty for auto-detect)"
    )
    async def translate(
        self,
        interaction: discord.Interaction,
        text: str,
        to_language: str,
        from_language: str = None
    ):
        """
        Translates text from one language to another.
        
        Args:
            text: The text to translate
            to_language: The destination language code (e.g., 'en', 'es', 'ja', 'fr')
            from_language: Optional source language code. If not provided, auto-detection is used.
        """
        self.logger.info(f"'translate' command used by {interaction.user.name}")

        if to_language not in LANGUAGE_MAP:
            await self._send_error(
                interaction,
                "Invalid Language",
                f"'{to_language}' is not a valid language code. Please use a valid language code (e.g., 'en', 'es', 'ja', 'fr').",
                ephemeral=True
            )
            return

        if from_language and from_language != 'auto' and from_language not in LANGUAGE_MAP:
            await self._send_error(
                interaction,
                "Invalid Language",
                f"'{from_language}' is not a valid source language code. Please use a valid language code, 'auto' for auto-detection, or leave empty for auto-detection.",
                ephemeral=True
            )
            return

        try:
            to_lang_name = LANGUAGE_MAP.get(to_language)
            if not from_language or from_language == 'auto':
                from_lang_name = 'auto'
            else:
                from_lang_name = LANGUAGE_MAP.get(from_language, 'auto')

            translator = GoogleTranslator(source=from_lang_name, target=to_lang_name)
            translated_text = translator.translate(text)

            to_lang_display = LANGUAGE_DISPLAY_NAMES.get(to_language, to_language)

            if not from_language or from_language == 'auto':
                from_lang_display = 'Auto-detected'
            else:
                from_lang_display = LANGUAGE_DISPLAY_NAMES.get(from_language, from_language)

            embed = self._create_embed(
                title="Translation Result",
                description=f"Translated from **{from_lang_display}** to **{to_lang_display}**"
            )

            embed.add_field(
                name=f"Original ({from_lang_display})",
                value=f"```{text}```",
                inline=False
            )
            embed.add_field(
                name=f"Translated ({to_lang_display})",
                value=f"```{translated_text}```",
                inline=False
            )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            self.logger.error(f"Translation error: {e}", exc_info=True)
            await self._send_error(
                interaction,
                "Translation Error",
                f"An error occurred while translating: {str(e)}",
                ephemeral=True
            )

    @translate.autocomplete('to_language')
    async def to_language_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        """Autocomplete for destination language."""
        return await self.language_autocomplete(interaction, current)

    @translate.autocomplete('from_language')
    async def from_language_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        """Autocomplete for source language (includes auto-detect option)."""
        if not current:
            auto_choice = [app_commands.Choice(name="Auto-detect (auto)", value="auto")]
            return auto_choice + self.language_choices[:24]
        
        current_lower = current.lower()
        if "auto" in current_lower:
            auto_choice = [app_commands.Choice(name="Auto-detect (auto)", value="auto")]
            filtered = [
                choice for choice in self.language_choices
                if current_lower in choice.name.lower() or current_lower in choice.value.lower()
            ]
            return (auto_choice + filtered)[:25]
        
        filtered = [
            choice for choice in self.language_choices
            if current_lower in choice.name.lower() or current_lower in choice.value.lower()
        ]
        return filtered[:25]


async def setup(bot: commands.Bot):
    await bot.add_cog(Translate(bot))
