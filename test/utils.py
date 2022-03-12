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

import os
import sys
import stat
import shutil
import logging

from importlib import reload

from typing import Tuple, Optional

from log.log_setup import LoggerManager, logger_init


def common_test_setup(custom_config: Optional[str] = None) -> Tuple[object, object, LoggerManager]:
    if custom_config:
        os.environ['ACTIVE_CONFIG'] = custom_config
    os.environ['TESTING'] = 'true'

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
    # Reload the logger
    reload(logging)

    # Reload sys after patching sys.stderr and sys.stdout for logger
    sys.stdout = stdout
    sys.stderr = stderr

    # # Change folder permissions and delete the directory.
    os.chmod('test/data', stat.S_IWUSR)
    shutil.rmtree('test/data')

    # Reset environment variables
    if 'ACTIVE_CONFIG' in os.environ:
        del os.environ['ACTIVE_CONFIG']
    del os.environ['TESTING']
