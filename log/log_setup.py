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

import re
import os
import sys
import shutil

from threading import Thread

from typing import Optional, Tuple

from configparser import ConfigParser

from multiprocessing import Queue, Manager, current_process

from logging import Logger
import logging
import logging.handlers

import log.globals


class LoggerManager:

    def __init__(self, logger_thread: Thread):
        self.logger_thread = logger_thread

    def terminate_logger(self):
        """
        This method terminates the logger thread. It should be called when log is complete during program cleanup.
        Returns:

        """
        # Trigger the logger thread to stop processing from the queue.
        log.globals.logger_queue.put(None)
        # Join the thread back to the main thread.
        self.logger_thread.join()

        # Shut down the handlers
        root = logging.getLogger()
        for handler in root.handlers:
            handler.close()
            root.removeHandler(handler)

        # Shutdown logging
        logging.shutdown()


class RedirectToLogger(object):
    """
    Used to redirect stdout and stderr to logger in _redirect_stdout_stderr
    """

    def __init__(self, logger, log_level=logging.INFO):
        self.logger = logger
        self.log_level = log_level
        self.value = None

    def write(self, message):
        self.value = message
        for line in message.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())

    def flush(self):
        pass

    def getvalue(self):
        return self.value


class CreateFileHandlerHandler(logging.Handler):

    def __init__(self, config: ConfigParser):
        super().__init__()
        self.config = config

        self.segregate_regex = re.compile('(LOGSEG\(.*?\))')
        self.seg_name_regex = re.compile('(?<=\()(.*)(?=\))')

    def _process_logseg(self, log: str) -> Tuple[str, str]:
        """
        This method processes a logseg log record.
        Args:
            log: The log string to be processed.

        Returns: A Tuple containing the final message and the segregate folder name for the log string.

        """
        segregate_folder_name = None
        if re.findall(self.segregate_regex, log):
            # Determine the segregate folder name defined in the log string.
            segregate_folder_name = re.findall(
                self.seg_name_regex,
                re.findall(self.segregate_regex, log)[0])[0]
            # Rewrite the log message to not include the segregation tag.
            final_message = re.sub(self.segregate_regex, '', log)
        else:
            final_message = log
        return final_message, segregate_folder_name

    def emit(self, record):
        """
        Create a file handler, attached to the logger instance.
        """
        try:
            # Handle logging to separate file, if requested:
            segregate_folder_name = None

            # Handle message property
            if hasattr(record, 'message'):
                record.message, name = self._process_logseg(record.message)
                segregate_folder_name = name if name else segregate_folder_name

            # Handle msg property
            if hasattr(record, 'msg'):
                record.msg, name = self._process_logseg(record.msg)
                segregate_folder_name = name if name else segregate_folder_name

            if segregate_folder_name:
                logger = logging.getLogger(segregate_folder_name)
                # Don't propagate to the root logger, this would cause infinite recursion.
                logger.propagate = False
                # Add a file handler to the logger instance for the segregate folder.
                _add_file_handler(config=self.config, instance=logger, log_formatter=_get_log_formatter(),
                                  folder_name=segregate_folder_name)
                logger.handle(record)
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)


def _add_file_handler(config: ConfigParser, instance, log_formatter, folder_name: Optional[str] = None):
    """

    Args:
        config:
        instance:
        log_formatter:
        folder_name:

    Returns:

    """
    # If the file handler doesn't already exist, create it.
    if not folder_name or folder_name and folder_name not in [x.name for x in instance.handlers]:
        # Create the directory for the logs if necessary.
        base_log_path = config.get('Logger', 'log_dir')
        if folder_name:
            log_path = f'{base_log_path}/{folder_name}'
        else:
            log_path = base_log_path
        if not os.path.isdir(log_path):
            os.makedirs(log_path)

        # Define the file handler.
        file_handler = logging.handlers.RotatingFileHandler(f"{log_path}/scheduled_vm.log",
                                                            maxBytes=config.getint('Logger', 'max_bytes'),
                                                            backupCount=config.getint('Logger', 'backup_count'))
        file_handler.set_name(folder_name)

        # Add the file handler.
        file_handler.setFormatter(log_formatter)
        instance.addHandler(file_handler)


def _get_log_formatter():
    # Define the formatter.
    return logging.Formatter("%(asctime)s: %(levelname)7s > %(message)s")


def _get_root_logger():
    """
    This function gets the root logger and sets its level.
    Returns:

    """
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    return root


def _redirect_stdout_stderr():
    """
    This function redirects the standard out and standard error to logger instances.
    Returns:

    """
    # Redirect stdout to a logger instance
    stdout_logger = get_logger('stdout')
    stdout_logger = RedirectToLogger(stdout_logger, logging.INFO)
    sys.stdout = stdout_logger

    # Redirect stderr to a logger instance
    stderr_logger = get_logger('stderr')
    stderr_logger = RedirectToLogger(stderr_logger, logging.WARNING)
    sys.stderr = stderr_logger


def _configure_logging_handlers(config: ConfigParser) -> Logger:
    # Get the root logger.
    root = _get_root_logger()

    # Define the formatter.
    log_formatter = _get_log_formatter()

    # Add the file handler
    _add_file_handler(config, root, log_formatter)

    # Create the handler that creates more file handlers.
    file_handler_handler = CreateFileHandlerHandler(config=config)
    root.addHandler(file_handler_handler)

    # Define the stream handler.
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(log_formatter)
    root.addHandler(stdout_handler)

    # Redirect stdout and stderr to a logger instance.
    _redirect_stdout_stderr()

    return root


def _lt(queue: Queue):
    """
    This function acts as the thread that listens to the logger queue and sends queued logs to the logger instance.
    Args:
        queue: A multiprocessing Queue, managed my a multiprocessing Manager.

    Returns:

    """
    while True:
        record = queue.get()
        if record is None:
            break
        logger = logging.getLogger(record.name)
        logger.handle(record)


def logger_init(config: ConfigParser) -> LoggerManager:
    """
    This function initializes a logger as well as a thread to process logs produced by concurrent processes. Logs
    from concurrent processes should be passed through the multiprocessing queue stored in log.globals.logger_queue.

    Args:
        config: A ConfigParser containing the configuration.

    Returns: A LoggerManager instance which can be used to terminate the logger thread at cleanup time.

    """
    logger_dir = config.get('Logger', 'log_dir')

    # Delete the directory if the config specifies to do so.
    if config.getboolean('Logger', 'pre_purge'):
        if os.path.isdir(logger_dir):
            shutil.rmtree(logger_dir)

    if not os.path.isdir(logger_dir):
        os.makedirs(logger_dir)

    log.globals.logger_queue = Manager().Queue()

    _configure_logging_handlers(config)

    logger_thread = Thread(target=_lt, args=(log.globals.logger_queue,))
    logger_thread.start()

    return LoggerManager(logger_thread=logger_thread)


def get_logger(name: str, queue: Optional[Queue] = None) -> Logger:
    """
    This function gets a logger instance.

    Usage:
    1) Call logger_init() and keep the LoggerManager for the life of the program.
    2) Import get_logger(__name__) wherever you want to use the logger.
    3) Use the logger, logger.info('your message')

    4) When using multiprocessing...

        import log.globals
        Pass log.globals.logger_queue as a parameter to the multiprocessing function explicitly
        (needed due to process spawning on Windows OS).

        e.g.
        pool = mp.Pool(processes=mp.cpu_count())
        pool.imap_unordered(func=partial(
            my_function,
            queue=log.globals.logger_queue,
            parameters=parameters
        ))
        pool.close()
        pool.join()

        Set up a logger instance from within the function that multiprocessing is being applied to. It will communicate
        with the root logger using the queue.

        e.g.
        def my_function(queue, parameters):
            multiprocessing_logger = get_logger(__name__, queue=queue)
            multiprocessing_logger.info('testing logger in multiprocessing')

    5) When you are finished logging, close the logger using the LoggerManager returned from logger_init() (step 1)

        e.g.
        logger_manager.terminate_logger()

    Args:
        name: The name for the logger.
        queue: A Queue instance generated by logger_init(), held in the variable log.globals.logger_queue

    Returns:

    """
    if current_process().name != 'MainProcess' and not queue:
        '''
        Don't create the logger, state reached may be due to Windows process spawning (imports may be re-evaluated
        upon spawn of a new process).
        '''
        pass
    elif queue is not None and current_process().name != 'MainProcess':
        # Set up the queue handler for the logger instance.
        queue_handler = logging.handlers.QueueHandler(queue)
        queue_handler.set_name(name=current_process().pid.__str__())

        # Get the root logger instance.
        root = _get_root_logger()

        # Redirect stdout to a logger instance
        _redirect_stdout_stderr()

        # Add the handler if it doesn't already exist.
        if queue_handler.name not in [x.name for x in root.handlers]:
            # Add the queue handler.
            root.addHandler(queue_handler)

    logger = logging.getLogger(name=name)

    return logger
