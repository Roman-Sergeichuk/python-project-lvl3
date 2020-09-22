import logging


def make_logging_level(level):  # pragma: no cover
    if level == 'debug' or level == 'DEBUG':
        logging_level = logging.DEBUG
    elif level == 'warning' or level == 'WARNING':
        logging_level = logging.WARNING
    elif level == 'error' or level == 'ERROR':
        logging_level = logging.ERROR
    elif level == 'critical' or level == 'CRITICAL':
        logging_level = logging.CRITICAL
    else:
        logging_level = logging.INFO
    return logging_level


def setup_log(logging_level, logfile='logfile.log'):  # pragma: no cover
    logging_level = make_logging_level(logging_level)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    formatter_console = logging.Formatter('%(message)s')
    console.setFormatter(formatter_console)
    logger.addHandler(console)
    f = logging.FileHandler(logfile)
    f.setLevel(logging_level)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    f.setFormatter(formatter)
    logger.addHandler(f)
    return logger
