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

def setup_logging():
    """Configures the logging for the entire application."""
    main_log_level_str = os.getenv('LOG_LEVEL_MAIN', 'INFO').upper()
    discord_log_level_str = os.getenv('LOG_LEVEL_DISCORD', 'INFO').upper()

    main_level = LOG_LEVELS.get(main_log_level_str, logging.INFO)
    discord_level = LOG_LEVELS.get(discord_log_level_str, logging.INFO)

    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        '[%(asctime)s] [%(name)-18s] [%(levelname)-7s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()

    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(handler)

    logging.getLogger('__main__').setLevel(main_level)

    logging.getLogger('discord').setLevel(discord_level)
    logging.getLogger('discord.http').setLevel(discord_level)

    logging.getLogger(__name__).info(
        f"Logging configured. Main level: {main_log_level_str}, Discord level: {discord_log_level_str}"
    )

