import argparse
import logging


def make_logging_level(level):  # pragma: no cover
    logging_level = logging.DEBUG
    if level == 'debug' or level == 'DEBUG':
        logging_level = logging.DEBUG
    elif level == 'warning' or level == 'WARNING':
        logging_level = logging.WARNING
    elif level == 'error' or level == 'ERROR':
        logging_level = logging.ERROR
    elif level == 'critical' or level == 'CRITICAL':
        logging_level = logging.CRITICAL
    return logging_level


def get_parser():  # pragma: no cover
    parser = argparse.ArgumentParser(description='Page loader')
    parser.add_argument('url')
    parser.add_argument(
        '-o',
        '--output',
        type=str,
        default='',
        help='set output directory'
    )
    parser.add_argument(
        '-l',
        '--level',
        type=str,
        default=None,
        choices=['debug', 'DEBUG', 'INFO', 'info', 'warning', 'WARNING',
                 'ERROR', 'error', 'critical', 'CRITICAL', None, ''],
        help='level of logging'
    )
    return parser
