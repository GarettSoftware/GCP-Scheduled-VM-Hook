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

from distutils.util import strtobool

from configparser import ConfigParser


def get_config() -> ConfigParser:
    """
    Determine and load the correct config file based on environment variables.
    """
    config = ConfigParser()

    # Retrieve the active config, if it is defined.
    active_config = os.environ['ACTIVE_CONFIG'] if 'ACTIVE_CONFIG' in os.environ else None

    # Manage config in test vs dev/prod environment.
    if "TESTING" in os.environ and strtobool(os.environ['TESTING']):
        if not active_config:
            # If testing mode is enabled and no active config is defined, use default test config in test dir.
            config.read('test/test.config')
        else:
            # Assume config is relative to test dir, since the config defined should be test specific.
            config.read(f'test/{active_config}.config')
    else:
        # If no TESTING variable defined, require an ACTIVE_CONFIG and assume config in configurations dir.
        assert active_config, "A config is required! Define the ACTIVE_CONFIG environment variable!"
        config.read(f'configurations/{active_config}.config')
    return config

