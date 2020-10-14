import logging
from page_loader.cli import make_logging_level


LOGFILE = 'logfile.log'


def setup(logging_level):  # pragma: no cover
    logging_level = make_logging_level(logging_level)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    formatter_console = logging.Formatter('%(message)s')
    console.setFormatter(formatter_console)
    logger.addHandler(console)
    f = logging.FileHandler(LOGFILE)
    f.setLevel(logging_level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    f.setFormatter(formatter)
    logger.addHandler(f)
    # return logger
