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

from functools import partial

from datetime import datetime

from configparser import ConfigParser
from configurations.config import get_config

from multiprocessing import Queue

import multiprocessing as mp

"""
Feel free to copy the code below into other files in your project to enable logging to log/logs.
Remember to use logger.info('Your message') or logger.warning('Your warning').
"""
from log.log_setup import get_logger, logger_init, LoggerManager
import log.globals
logger = get_logger(__name__)


class SchedulerHook:

    def __init__(self):
        self.config: ConfigParser = get_config()
        self.logger_manager: LoggerManager = logger_init(self.config)

    @staticmethod
    def _test_process(string: str, queue: Queue) -> None:
        multiprocessing_logger = get_logger(__name__, queue=queue)
        multiprocessing_logger.info(string)

    def execute(self) -> None:
        """
        This function gets called by a chron tab shortly after the virtual machine in GCP wakes up.

        Users of this script should either
        1) Build their application on top of this script directly (Clone the repository)
        2) Copy the hook directory in this repository into an existing repository, and modify this execute() function to
        import and call your existing code.
        """
        logger.info("Scheduled script started.")
        start_time: datetime = datetime.now()

        logger.info("Hello World!")
        """
        Example 1
        logger.info("Hello World!")
        """

        pool = mp.Pool(processes=mp.cpu_count())
        pool.imap_unordered(func=partial(
            self._test_process,
            queue=log.globals.logger_queue,
        ), iterable=['1', '2', '3', '4', '5'])
        pool.close()
        pool.join()

        """
        Example 2
        from your_code import main
        main()
        """

        self.logger_manager.terminate_logger()

        end_time: datetime = datetime.now()
        elapsed_time = end_time - start_time
        logger.info(f"Scheduled script completed in {elapsed_time}")


if __name__ == '__main__':
    # Explicitly set process start method to get consistent behavior across platforms.
    mp.set_start_method('spawn')

    hook: SchedulerHook = SchedulerHook()
    hook.execute()
