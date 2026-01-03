import logging
import sys

logger = logging.getLogger(__name__)
default_level = logging.WARNING
logger.level = default_level

def set_log_level(logging_level):
    # For some reason setting the level in basicConfig fails?
    logging.getLogger(__name__).level = logging_level

    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(stream=sys.stdout)],
    )
