import logging
import time
import os
import threading

project_root = os.path.join(os.path.dirname(__file__))


def main():
    # create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # create console handler
    console_hldr = logging.StreamHandler()
    console_hldr.setLevel(logging.DEBUG)
    # create file handler
    file_hldr = logging.FileHandler(os.path.join(project_root, 'main.log'))
    file_hldr.setLevel(logging.INFO)
    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - [%(levelname)s] %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
    # add formatter to console_hldr and file_hldr
    console_hldr.setFormatter(formatter)
    file_hldr.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(console_hldr)
    logger.addHandler(file_hldr)

    thread_list = []

    logger.info('Program started.')

    try:
        pass
    except:
        logger.exception('Program finished with exceptions.')
    else:
        logger.info('Program finished successfully.')


if __name__ == '__main__':
    main()
