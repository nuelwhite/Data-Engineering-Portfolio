import logging



logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def setup_logger(log_file):
    """
    Setup the logger with the given log file.
    """
    # create handlers if there are no handlers
    if not logger.handlers:
        #create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # create file handler 
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG).setLevel(logging.INFO)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s')

        # add formatter to handlers
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
