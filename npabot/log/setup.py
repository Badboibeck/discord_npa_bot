import logging

from loguru import logger

from dixxbot.config import BotConfig


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logger(config: BotConfig):
    the_logger = logging.getLogger("discord")
    the_logger.setLevel(config.log.level)
    the_logger.addHandler(InterceptHandler())
    return the_logger
