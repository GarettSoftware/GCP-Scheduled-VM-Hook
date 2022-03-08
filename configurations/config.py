import os
from configparser import ConfigParser


def get_config() -> ConfigParser:
    """
    Determine and load the correct config file based on an environment variable
    """
    active_config = os.environ['ACTIVE_CONFIG']
    config = ConfigParser()
    config.read(f'configurations/{active_config}.config')
    return config
