from datetime import datetime

"""
Feel free to copy the code below into other files in your project to enable logging to hooks/logs.
Remember to use logger.info('Your message') or logger.warning('Your warning').
"""
from hook.log_setup import get_logger
logger = get_logger(__name__)


class SchedulerHook:

    def __init__(self):
        pass

    @staticmethod
    def execute() -> None:
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
        """
        Example 2
        from your_code import main
        main()
        """

        end_time: datetime = datetime.now()
        elapsed_time = end_time - start_time
        logger.info(f"Scheduled script completed in {elapsed_time}")


if __name__ == '__main__':
    hook: SchedulerHook = SchedulerHook()
    hook.execute()
