import logging

logger = None


def get_logger():
    global logger
    if logger is not None:
        return logger
    logger = logging.getLogger("survey")
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.INFO)
    return logger
