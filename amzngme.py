import argparse
import os
import sys
import re
import logging
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

def handle_args():
    parser = argparse.ArgumentParser(
        description="Use web drivers to open all daily giveaways on Amazon.")
    parser.add_argument(
        "--download-chromedriver-binary",
        action='store_true',
        default=False,
        dest="download_binary",
        help="Download a local binary file for the chrome web driver."
    )
    parser.add_argument(
        "--debug",
        action='store_true',
        default=False,
        dest="enable_debug",
        help="Enable extensive logging.")

    args = vars(parser.parse_args())

    input_args = dict(args)
    _LOGGER.debug("Input args: %s", input_args)

    return (args['download_binary'], args['enable_debug'])

def main():
	(download_binary, enable_debug) = handle_args()

	setup_logging(enable_debug)

def setup_logging(enable_debug=False):
    logging_level = logging.DEBUG if enable_debug else logging.INFO
    root_path = os.path.dirname(
        os.path.abspath(sys.modules['__main__'].__file__))
    log_path = os.path.join(root_path, 'amzngme.log')
    logging.basicConfig(
        level=logging_level,
        format='[%(levelname)s: %(asctime)s] %(name)-12s %(message)s',
        datefmt='%m-%d %H:%M',
        filename=log_path,
        filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    logging.getLogger('').addHandler(console)  # add handler to the root logger

if __name__ == '__main__':
	main()