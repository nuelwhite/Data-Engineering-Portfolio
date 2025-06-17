import logging
import os
from pathlib import Path


def setup_logger(log_file):
    """
    Setup the logger with the given log file.
    
    Args:
        log_file (str): Path to the log file
        
    Returns:
        logging.Logger: Configured logger instance
    """
    try:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
            
        # Get logger instance
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers if any
        if logger.handlers:
            logger.handlers.clear()
            
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s'
        )
        
        # Add formatter to handlers
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
        
    except Exception as e:
        print(f"Error setting up logger: {str(e)}")
        # Return a basic logger if setup fails
        basic_logger = logging.getLogger(__name__)
        basic_logger.setLevel(logging.INFO)
        return basic_logger
