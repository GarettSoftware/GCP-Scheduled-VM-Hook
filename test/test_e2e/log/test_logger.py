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

import datetime

import numpy as np

from functools import partial

from threading import Thread

import multiprocessing as mp
from multiprocessing import Queue

from unittest import TestCase

from test.utils import common_test_setup, common_test_teardown

import log.globals
from log.log_setup import get_logger


class TestLogger(TestCase):
    """
    This class is responsible for testing the logger for concurrency issues.
    """

    def tearDown(self) -> None:
        common_test_teardown(logger_manager=self.logger_manager, stdout=self.stdout, stderr=self.stderr)

    def test_1(self):
        self.stdout, self.stderr, self.logger_manager = common_test_setup()

        sequential_logger = get_logger(__name__)
        sequential_logger.info(f'Starting thread...')

        _test_1_helper(sequential_logger)

        # Run assertions on log files.
        with open('test/data/log/logs/thread_1/scheduled_vm.log', 'r') as f:
            content = f.readlines()
            content_len = len(content)
            assert content_len == 1, f"Only one log should be in thread_1 log file. Found {content_len}.\n{content}"
        with open('test/data/log/logs/thread_2/scheduled_vm.log', 'r') as f:
            content = f.readlines()
            content_len = len(content)
            assert content_len == 1, f"Only one log should be in thread_2 log file. Found {content_len}.\n{content}"
        with open('test/data/log/logs/scheduled_vm.log', 'r') as f:
            content = f.readlines()
            content_len = len(content)
            assert content_len == 53, f"Only 53 logs should be in log file. Found {content_len}.\n{content}"

    def test_2(self):
        # Use custom configurations for this test.
        self.stdout, self.stderr, self.logger_manager = common_test_setup(custom_config='test_e2e/log/test_2')

        _test_2_helper()

        with open('test/data/log/logs/scheduled_vm.log', 'r') as f:
            content = f.readlines()
            content_len = len(content)
            assert content_len == 1, f"Only one log should be in log file. Found {content_len}.\n{content}"
        with open('test/data/log/logs/scheduled_vm.log.1', 'r') as f:
            content = f.readlines()
            content_len = len(content)
            assert content_len == 1, f'Only one log should be in log file. Found {content_len}.\n{content}'


# ---- Test 1 helpers ---- #

def _test_1_helper(sequential_logger):
    iterable = np.arange(start=0, stop=10)

    for i in iterable:
        sequential_logger.info(f'sequential logger: {i}')

    # Start up new threads for the two inbound queues.
    t1 = Thread(target=_test_1_threading_helper,
                args=(1, iterable),
                daemon=True)
    t2 = Thread(target=_test_1_threading_helper,
                args=(2, iterable),
                daemon=True)
    t1.start()
    t2.start()

    # Join threads back to main thread.
    t1.join()
    t2.join()


def _test_1_threading_helper(thread_num: int, iterable: np.ndarray):
    thread_logger = get_logger(f'{__name__}_{thread_num}')

    thread_logger.info(f'LOGSEG(thread_{thread_num})Thread {thread_num} started')

    pool = mp.Pool(processes=mp.cpu_count())
    pool.map(func=partial(_test_1_multiprocessing_helper,
                          thread_num=thread_num,
                          logger_queue=log.globals.logger_queue),
             iterable=iterable)
    pool.close()
    pool.join()


def _test_1_multiprocessing_helper(i: int, thread_num: int, logger_queue: Queue):
    multiprocessing_logger = get_logger(name=__name__, queue=logger_queue)
    multiprocessing_logger.info(f'Thread: {thread_num}, Multiprocessing logger: {i}')

    # Print to sys.stdout to check if logger redirect is working.
    print(f'SEGLOG(thread_{thread_num})Thread: {thread_num}, Multiprocessing sys.stdout logger: {i}')


# ---- Test 2 helpers ---- #

def _test_2_helper():
    # Create a list of times to print so that processes attempt to print at exact same time.
    current_time = datetime.datetime.now()
    print_time = current_time + datetime.timedelta(seconds=5)

    processes = []
    for i in range(2):
        processes.append(mp.Process(target=partial(_test_2_process_helper,
                                                   process_num=i,
                                                   print_time=print_time,
                                                   logger_queue=log.globals.logger_queue)))
    # Start the processes.
    for process in processes:
        process.start()
    # Join processes back to main thread
    for process in processes:
        process.join()
    # Close the processes.
    for process in processes:
        process.close()


def _test_2_process_helper(process_num: int, print_time: datetime.datetime, logger_queue: Queue):
    multiprocessing_logger = get_logger(name=__name__, queue=logger_queue)

    # Wait until the print time arrives.
    while datetime.datetime.now() < print_time:
        pass

    # Print now that the processes are in sync.
    multiprocessing_logger.info(f'Process: {process_num} printing at {datetime.datetime.now()}')
