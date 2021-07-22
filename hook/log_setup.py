import sys
import logging
import logging.handlers


def get_logger(name):
    """
    # -- Usage --
    # Import this function.
    from hook.log_setup import get_logger
    # Create the logger
    logger = get_logger(__name__)
    # Use the logger
    logger.info(f"message: {variable}.")

    :param name: __name__ attribute of logger usage file.
    :return:
    """
    # Set the base logger log level
    logging.getLogger().setLevel(logging.INFO)

    # Set the log format
    log_formatter = logging.Formatter("%(asctime)s: %(levelname)7s > %(message)s")

    # Create a handler for writing the logger to stderr.
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(log_formatter)

    # Create a handler for the rotating log file.
    file_handler = logging.handlers.RotatingFileHandler("hook/logs/scheduled_vm.log", maxBytes=100000, backupCount=6)
    file_handler.setFormatter(log_formatter)

    logger = logging.getLogger(name)
    logger.addHandler(stderr_handler)
    logger.addHandler(file_handler)
    return logger


class RedirectToLogger(object):
    """
    Used to redirect stdout and stderr to logger in hook/__init__.
    """
    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level

    def write(self, message):
        for line in message.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass
