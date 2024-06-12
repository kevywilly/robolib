import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("robolib")
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


def pretty(text):
    logger.info(
        f"""
        ******************************************************************
        \t{text}
        ******************************************************************
        """
    )
