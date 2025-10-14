import logging
import os
import sys

LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and better formatting"""

    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m',       # Reset
        'BOLD': '\033[1m',        # Bold
        'DIM': '\033[2m',         # Dim
    }

    SYMBOLS = {
        'DEBUG': '🔍',
        'INFO': '✓',
        'WARNING': '⚠',
        'ERROR': '✗',
        'CRITICAL': '🔥',
    }

    def __init__(self, use_colors=True, use_symbols=True):
        super().__init__()
        self.use_colors = use_colors and sys.stdout.isatty()
        self.use_symbols = use_symbols

    def format(self, record):
        name = record.name
        if name.startswith('cogs.'):
            # cogs.information -> info
            # cogs.stats.cog_db_functions -> stats.db
            parts = name.split('.')
            if len(parts) == 2:
                name = parts[1][:12]  # Shorten to 12 chars
            elif len(parts) >= 3 and parts[-1] == 'cog_db_functions':
                name = f"{parts[1][:8]}.db"
            else:
                name = '.'.join(parts[1:])[:15]
        elif name == '__main__':
            name = 'main'
        elif name.startswith('discord.'):
            name = name.replace('discord.', 'd.')[:12]
        elif name.startswith('database.'):
            name = name.replace('database.', 'db.')[:12]
        else:
            name = name[:15]  # Limit length

        level_name = record.levelname
        color = self.COLORS.get(level_name, '') if self.use_colors else ''
        symbol = self.SYMBOLS.get(level_name, ' ') if self.use_symbols else ''
        reset = self.COLORS['RESET'] if self.use_colors else ''
        dim = self.COLORS['DIM'] if self.use_colors else ''

        timestamp = self.formatTime(record, '%H:%M:%S')

        message = record.getMessage()

        extra_line = ''
        if 'Loading Cogs' in message or 'Cogs Loaded' in message or 'Logged in as' in message:
            extra_line = '\n'

        formatted = (
            f"{dim}{timestamp}{reset} "
            f"{color}{symbol} {level_name:<9}{reset} "
            f"{dim}[{name:15}]{reset} "
            f"{message}"
            f"{extra_line}"
        )

        if record.exc_info:
            formatted += '\n' + self.formatException(record.exc_info)

        return formatted


def setup_logging():
    """Configures the logging for the entire application."""
    main_log_level_str = os.getenv('LOG_LEVEL', os.getenv('LOG_LEVEL_MAIN', 'INFO')).upper()
    discord_log_level_str = os.getenv('LOG_LEVEL_DISCORD', 'WARNING').upper()

    main_level = LOG_LEVELS.get(main_log_level_str, logging.INFO)
    discord_level = LOG_LEVELS.get(discord_log_level_str, logging.WARNING)

    handler = logging.StreamHandler(sys.stdout)

    formatter = ColoredFormatter(use_colors=True, use_symbols=True)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)

    logging.getLogger('__main__').setLevel(main_level)
    logging.getLogger('discord').setLevel(discord_level)
    logging.getLogger('discord.http').setLevel(discord_level)
    logging.getLogger('discord.gateway').setLevel(discord_level)
    logging.getLogger('discord.client').setLevel(discord_level)

    logger = logging.getLogger('main')
    logger.info('═' * 60)
    logger.info(f'Task Manager Bot Starting')
    logger.info(f'Log Level: {main_log_level_str} | Discord: {discord_log_level_str}')
    logger.info('═' * 60)
