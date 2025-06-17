import logging
import os
from pathlib import Path
from datetime import datetime


def setup_logger(log_name, log_dir='logs'):
    """
    Setup the logger with the given log name and directory.
    
    Args:
        log_name (str): Name of the log file (e.g., 'patients_pipeline', 'billing_pipeline')
        log_dir (str): Parent directory for all log files (default: 'logs')
        
    Returns:
        logging.Logger: Configured logger instance
    """
    try:
        # Create timestamp for log file with hyphen separators
        timestamp = datetime.now().strftime('%Y-%m-%d')
        
        # Create log directory structure
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)
        
        # Create log file path with timestamp
        log_file = log_path / f"{log_name}_{timestamp}.log"
        
        # Get logger instance
        logger = logging.getLogger(log_name)
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
        
        logger.info(f"Logger initialized. Log file: {log_file}")
        return logger
        
    except Exception as e:
        print(f"Error setting up logger: {str(e)}")
        # Return a basic logger if setup fails
        basic_logger = logging.getLogger(log_name)
        basic_logger.setLevel(logging.INFO)
        return basic_logger
