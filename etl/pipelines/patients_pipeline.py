import logging
import pandas as pd
from sqlalchemy import text
from etl.utils.db_config import DatabaseConfig
from etl.utils.transformations import DataTransformer
from etl.utils.idempotency import IdempotencyHandler
from etl.utils.logger import setup_logger

# Setup logger for tracking pipeline execution
#logger = logging.getLogger(__name__)
logger = setup_logger('patients_pipeline')


# Pipeline configuration constants
SOURCE_TABLE = 'patients_demographics'  # Source table in MySQL
TARGET_TABLE = 'patients_demographics'  # Target table in PostgreSQL
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
    Process a batch of patient records.
    
    Args:
        batch: Batch of records to process
        transformer: DataTransformer instance
        
    Returns:
        pd.DataFrame: Processed batch
    """
    try:
        # Convert batch to DataFrame for easier manipulation
        df = pd.DataFrame(batch)
        
        # Standardize date formats for consistency
        df = transformer.standardize_dates(
            df, 
            ['date_of_birth', 'updated_at']
        )
        
        # Remove any duplicate records
        df = transformer.remove_duplicates(df)
        
        # Split address into components (street, city, state, zip)
        df = transformer.split_address(df, 'address')
        
        # Standardize phone number format
        df = transformer.standardize_phone(df, 'phone_number')
        
        # Handle missing values with appropriate strategies
        df = transformer.handle_missing_values(
            df,
            numeric_columns=['insurance_number'],  # Fill with 0 or median
            categorical_columns=['gender', 'blood_type'],  # Fill with mode
            date_columns=['date_of_birth', 'updated_at']  # Fill with current date
        )
        
        return df
        
    except Exception as e:
        logger.error(f"Error processing batch: {str(e)}")
        raise

def run_pipeline():
    """Run the patients data pipeline"""
    try:
        logger.info("Starting patients data pipeline...")
        
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
                'patient_id',  # Primary key for tracking progress
                BATCH_SIZE
            ):
                try:
                    # Transform the batch of records
                    processed_batch = process_batch(batch, transformer)
                    logger.info(f"Processing batch with {len(processed_batch)} records (DataFrame shape: {processed_batch.shape})")
                    logger.info(f"DataFrame columns: {processed_batch.columns.tolist()}")
                    
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
            
            logger.info("Patients data pipeline completed successfully")
            
        finally:
            # Clean up database connections
            mysql_engine.dispose()
            pg_engine.dispose()
            
    except Exception as e:
        logger.error(f"Error in patients pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    # Execute the pipeline
    run_pipeline() 