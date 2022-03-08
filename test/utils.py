import os
import sys
import stat

import shutil

from typing import Tuple

from log.log_setup import LoggerManager, logger_init


def common_test_setup() -> Tuple[object, object, LoggerManager]:
    os.environ['ACTIVE_CONFIG'] = 'test'

    # Create a test log directory
    if not os.path.isdir('test/data'):
        os.makedirs('test/data')

    # Cache the stdout and stderr, they are monkey patched when logging.
    stdout = sys.stdout
    stderr = sys.stderr
    logger_manager: LoggerManager = logger_init()

    return stdout, stderr, logger_manager


def common_test_teardown(logger_manager: LoggerManager, stdout, stderr):
    # Terminate the logger.
    logger_manager.terminate_logger()

    # Reload sys after patching sys.stderr and sys.stdout for logger
    sys.stdout = stdout
    sys.stderr = stderr

    # # Change folder permissions and delete the directory.
    os.chmod('test/data', stat.S_IWUSR)
    shutil.rmtree('test/data')
