import logging
from pathlib import Path
from typing import Optional

def setup_logger(logger_name: str = 'pipelines', log_file_name: Optional[str] = None) -> logging.Logger:
    """Configure and return a logger with both file and console handlers, and also a main pipeline log handler.
    
    This function sets up a logger with the following features:
    - File handler writing to logs/{log_file_name or logger_name}.log at INFO level
    - File handler writing to logs/main_pipeline.log at INFO level (shared by all loggers)
    - Console handler at DEBUG level
    - Automatic creation of logs directory if it doesn't exist
    - Error handling for file handler setup
    - Prevention of duplicate handlers for each logger
    
    Args:
        logger_name (str): Name of the logger. Default is 'pipelines'.
        log_file_name (Optional[str]): Name of the log file (without path). If not provided, uses logger_name+'.log'.
    
    Returns:
        logging.Logger: The configured logger instance
    
    Note:
        The logger will write to both a file and console, with different log levels
        for each. File logging is at INFO level while console logging is at DEBUG level.
        All loggers also write to logs/main_pipeline.log for a combined log.
    """
    # Create a temporary logger for setup errors
    temp_logger = logging.getLogger(f'setup_{logger_name}')
    temp_logger.setLevel(logging.ERROR)
    temp_handler = logging.StreamHandler()
    temp_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    temp_logger.addHandler(temp_handler)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # Avoid adding multiple handlers to the logger if it already has one
    if not logger.handlers:
        # Create logs directory if it doesn't exist
        log_dir = Path(__file__).parent.parent / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # Determine log file name
        if log_file_name is None:
            log_file_name = f'{logger_name}.log'
        log_file = log_dir / log_file_name
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
        except Exception as e:
            temp_logger.error(f"Error setting up file handler: {e}")
            file_handler = None

        # Main pipeline log handler (shared log file for all loggers)
        main_pipeline_log_file = log_dir / 'main_pipeline.log'
        # Prevent duplicate main pipeline handlers by checking all handlers
        main_pipeline_handler_exists = any(
            isinstance(h, logging.FileHandler) and getattr(h, 'baseFilename', None) == str(main_pipeline_log_file)
            for h in logger.handlers
        )
        if not main_pipeline_handler_exists:
            try:
                main_pipeline_handler = logging.FileHandler(main_pipeline_log_file)
                main_pipeline_handler.setLevel(logging.INFO)
                main_pipeline_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                logger.addHandler(main_pipeline_handler)
            except Exception as e:
                temp_logger.error(f"Error setting up main pipeline file handler: {e}")

        # console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        if file_handler:
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Clean up temporary logger
    temp_logger.removeHandler(temp_handler)
    
    return logger


        
    
