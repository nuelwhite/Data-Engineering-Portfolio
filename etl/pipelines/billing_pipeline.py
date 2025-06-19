import logging
import pandas as pd
from sqlalchemy import text
from etl.utils.db_config import DatabaseConfig
from etl.utils.transformations import DataTransformer
from etl.utils.idempotency import IdempotencyHandler
from etl.utils.logger import setup_logger

# Setup logger for tracking pipeline execution
logger = setup_logger('billing_pipeline')

# Pipeline configuration constants
SOURCE_TABLE = 'billing_data'  # Source table in MySQL
TARGET_TABLE = 'billing_data'  # Target table in PostgreSQL
BATCH_SIZE = 500  # Number of records to process in each batch

def create_target_table(mysql_engine, pg_engine):
    """Create the target table in PostgreSQL if it doesn't exist"""
    try:
        # Check if table exists in PostgreSQL
        check_query = f"""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = '{TARGET_TABLE}'
            );
        """
        with pg_engine.connect() as connection:
            table_exists = connection.execute(text(check_query)).scalar()
        
        if not table_exists:
            # Fetch a single record to get the table schema
            query = f"SELECT * FROM {SOURCE_TABLE} LIMIT 1"
            with mysql_engine.connect() as connection:
                sample_data = pd.read_sql(query, connection)
            
            # Create the target table with the same schema
            sample_data.head(0).to_sql(
                TARGET_TABLE,
                pg_engine,
                if_exists='fail',  # Fail if table exists
                index=False  # Don't include index column
            )
            
            logger.info(f"Created target table: {TARGET_TABLE}")
        else:
            logger.info(f"Target table {TARGET_TABLE} already exists")
        
    except Exception as e:
        logger.error(f"Error creating target table: {str(e)}")
        raise

def process_batch(batch, transformer):
    """
    Process a batch of billing records.
    
    Args:
        batch: Batch of records to process
        transformer: DataTransformer instance
        
    Returns:
        pd.DataFrame: Processed batch
    """
    try:
        # Convert batch to DataFrame for easier manipulation
        df = pd.DataFrame(batch)
        
        # Standardize date formats
        df = transformer.standardize_dates(df, ['updated_at'])
        
        # Remove any duplicate records
        df = transformer.remove_duplicates(df)
        
        # Convert amount to decimal with 2 decimal places
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce').round(2)
        
        # Standardize payment status values
        df['payment_status'] = df['payment_status'].str.strip().str.title()
        
        # Standardize service codes to uppercase
        df['service_code'] = df['service_code'].str.strip().str.upper()
        
        # Handle missing values
        df = transformer.handle_missing_values(
            df,
            numeric_columns=['amount'],  # Fill with 0
            categorical_columns=['payment_status', 'service_code'],  # Fill with mode
            date_columns=['updated_at']  # Fill with current date
        )
        
        return df
        
    except Exception as e:
        logger.error(f"Error processing batch: {str(e)}")
        raise

def run_pipeline():
    """Run the billing data pipeline"""
    try:
        logger.info("Starting billing data pipeline...")
        
        # Initialize database connections
        mysql_engine = DatabaseConfig.get_mysql_connection()  # Source database
        pg_engine = DatabaseConfig.get_postgres_connection()  # Target database
        
        # Initialize utility handlers
        transformer = DataTransformer()  # For data transformations
        idempotency = IdempotencyHandler()  # For tracking processed records
        
        try:
            # Create target table if it doesn't exist
            create_target_table(mysql_engine, pg_engine)
            
            # Process data in batches for memory efficiency
            for batch, last_id in idempotency.process_in_batches(
                mysql_engine,
                SOURCE_TABLE,
                'invoice_id',  # Primary key for tracking progress
                BATCH_SIZE
            ):
                try:
                    # Transform the batch of records
                    processed_batch = process_batch(batch, transformer)
                    
                    if processed_batch.empty:
                        logger.warning(f"Batch up to ID {last_id} is empty after transformation. Skipping write to database.")
                        continue
                    
                    # Load transformed data to target database
                    processed_batch.to_sql(
                        TARGET_TABLE,
                        pg_engine,
                        if_exists='append',  # Append new records
                        index=False  # Don't include index column
                    )
                    
                    logger.info(f"Processed batch up to ID: {last_id}")
                    
                except Exception as e:
                    logger.error(f"Error processing batch: {str(e)}")
                    # Mark batch as failed in tracking system
                    idempotency.update_processing_status(
                        SOURCE_TABLE,
                        last_id,
                        len(batch),
                        status='failed'
                    )
                    raise
            
            logger.info("Billing data pipeline completed successfully")
            
        finally:
            # Clean up database connections
            mysql_engine.dispose()
            pg_engine.dispose()
            
    except Exception as e:
        logger.error(f"Error in billing pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    run_pipeline()