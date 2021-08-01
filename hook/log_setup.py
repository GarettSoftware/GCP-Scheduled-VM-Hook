"""
MIT License

Copyright (c) 2021 Garett MacGowan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys
import logging
import logging.handlers

# Set the base logger log level
logging.getLogger().setLevel(logging.INFO)

# Set the log format
log_formatter = logging.Formatter("%(asctime)s: %(levelname)7s > %(message)s")

# Create a handler for writing the logger to stderr.
stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setFormatter(log_formatter)

# Create a handler for the rotating log file.
file_handler = logging.handlers.RotatingFileHandler("hook/logs/scheduled_vm.log", maxBytes=10000000, backupCount=6)
file_handler.setFormatter(log_formatter)


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
