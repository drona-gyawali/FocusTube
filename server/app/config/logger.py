import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

current_date = datetime.now().strftime("%Y-%m-%d")


LOG_DIR = "logs"
LOG_FILE = f"app_{current_date}.log"
LOG_PATH = os.path.join(LOG_DIR, LOG_FILE)

os.makedirs(LOG_DIR, exist_ok=True)

formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(name)s - %(message)s", "%Y-%m-%d %H:%M:%S"
)

file_handler = RotatingFileHandler(LOG_PATH, maxBytes=5 * 1024 * 1024, backupCount=5)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.propagate = False


def get_logger(name: str):
    """
    Returns a logger instance with the specified name.

    This function ensures that each logger is configured with the same
    rotating file handler and formatter defined above. If the logger
    does not already have handlers, it attaches the shared file handler.
    This helps to keep log formatting and output consistent across modules.

    Args:
        name (str): The name of the logger, typically __name__ of the module.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        logger.addHandler(file_handler)
    return logger
