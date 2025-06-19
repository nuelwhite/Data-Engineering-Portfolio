import os
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Setup logger
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Database configuration class for managing database connections"""
    
    @staticmethod
    def get_mysql_connection():
        """
        Create and return a MySQL database connection using SQLAlchemy
        
        Returns:
            sqlalchemy.engine.Engine: MySQL database engine
        """
        try:
            # MySQL connection parameters
            mysql_config = {
                'drivername': 'mysql+pymysql',
                'username': os.getenv('MYSQL_DB_USER'),
                'password': os.getenv('MYSQL_DB_PASSWORD'),
                'host': os.getenv('MYSQL_DB_HOST'),
                'port': os.getenv('MYSQL_DB_PORT'),
                'database': os.getenv('MYSQL_DB_NAME')
            }
            
            # Create connection URL
            connection_url = URL.create(**mysql_config)
            
            # Create engine
            engine = create_engine(connection_url)
            
            # Test connection
            with engine.connect() as connection:
                logger.info("Successfully connected to MySQL database")
                return engine
                
        except Exception as e:
            logger.error(f"Failed to connect to MySQL database: {str(e)}")
            raise
    
    @staticmethod
    def get_postgres_connection():
        """
        Create and return a PostgreSQL database connection using SQLAlchemy
        
        Returns:
            sqlalchemy.engine.Engine: PostgreSQL database engine
        """
        try:
            # PostgreSQL connection parameters
            postgres_config = {
                'drivername': 'postgresql',
                'username': os.getenv('POSTGRES_USER'),
                'password': os.getenv('POSTGRES_PASSWORD'),
                'host': os.getenv('POSTGRES_HOST'),
                'port': os.getenv('POSTGRES_PORT'),
                'database': os.getenv('POSTGRES_DB')
            }
            
            # Create connection URL
            connection_url = URL.create(**postgres_config)
            
            # Create engine
            engine = create_engine(connection_url)
            
            # Test connection
            with engine.connect() as connection:
                logger.info("Successfully connected to PostgreSQL database")
                return engine
                
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL database: {str(e)}")
            raise


