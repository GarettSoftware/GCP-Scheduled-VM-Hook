import sys
import logging

from hook.log_setup import get_logger
from hook.log_setup import RedirectToLogger

logger = get_logger(__name__)

# Redirect stdout to a logger instance
stdout_logger = get_logger('stdout')
stdout_logger = RedirectToLogger(stdout_logger, logging.INFO)
sys.stdout = stdout_logger
# Redirect stderr to a logger instance
stderr_logger = get_logger('stderr')
stderr_logger = RedirectToLogger(stderr_logger, logging.WARNING)
sys.stderr = stderr_logger
