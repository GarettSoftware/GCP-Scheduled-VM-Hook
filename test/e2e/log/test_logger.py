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

    def setUp(self) -> None:
        self.stdout, self.stderr, self.logger_manager = common_test_setup()

    def tearDown(self) -> None:
        common_test_teardown(logger_manager=self.logger_manager, stdout=self.stdout, stderr=self.stderr)

    def test_logger_concurrency(self):
        sequential_logger = get_logger(__name__)
        sequential_logger.info(f'Starting thread...')

        _test_helper(sequential_logger)

        # Run assertions on log files.
        with open('test/data/log/logs/thread_1/scheduled_vm.log', 'r') as f:
            content = f.readlines()
            content_len = len(content)
            assert content_len == 1, f"Only one log should be in thread_1 log file. Found {content_len}"
            # assert content == ""
        with open('test/data/log/logs/thread_2/scheduled_vm.log', 'r') as f:
            content = f.readlines()
            content_len = len(content)
            assert content_len == 1, f"Only one log should be in thread_2 log file. Found {content_len}"
        with open('test/data/log/logs/scheduled_vm.log', 'r') as f:
            content = f.readlines()
            content_len = len(content)
            assert content_len == 53, f"Only 53 logs should be in log file. Found {content_len}"


def _test_helper(sequential_logger):
    iterable = np.arange(start=0, stop=10)

    for i in iterable:
        sequential_logger.info(f'sequential logger: {i}')

    # Start up new threads for the two inbound queues.
    t1 = Thread(target=_threading_helper,
                args=(1, iterable),
                daemon=True)
    t2 = Thread(target=_threading_helper,
                args=(2, iterable),
                daemon=True)
    t1.start()
    t2.start()

    # Join threads back to main thread.
    t1.join()
    t2.join()


def _threading_helper(thread_num: int, iterable: np.ndarray):
    thread_logger = get_logger(f'{__name__}_{thread_num}', segregate_folder=f'thread_{thread_num}')

    thread_logger.info(f'Thread {thread_num} started')

    pool = mp.Pool(processes=mp.cpu_count())
    pool.map(func=partial(_multiprocessing_helper,
                          thread_num=thread_num,
                          logger_queue=log.globals.logger_queue),
             iterable=iterable)
    pool.close()
    pool.join()


def _multiprocessing_helper(i: int, thread_num: int, logger_queue: Queue):
    multiprocessing_logger = get_logger(name=__name__, queue=logger_queue)
    multiprocessing_logger.info(f'Thread: {thread_num}, Multiprocessing logger: {i}')

    # Print to sys.stdout to check if logger redirect is working.
    print(f'Thread: {thread_num}, Multiprocessing sys.stdout logger: {i}')
