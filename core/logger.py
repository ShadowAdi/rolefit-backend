import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    logger = logging.getLogger("Tracer-logger")

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "logs")

    os.makedirs(LOG_DIR, exist_ok=True)

    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] "
        "[%(filename)s:%(lineno)d] - %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    info_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "info.log"),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(formatter)

    warn_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "warn.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=3
    )
    warn_handler.setLevel(logging.WARNING)
    warn_handler.setFormatter(formatter)

    error_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "error.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(info_handler)
    logger.addHandler(warn_handler)
    logger.addHandler(error_handler)

    return logger


logger = setup_logger()