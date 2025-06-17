import logging
from sqlalchemy import text
from datetime import datetime

# Initialize logger for tracking pipeline operations
logger = logging.getLogger(__name__)

class IdempotencyHandler:
    """Handles idempotency in data pipelines to prevent duplicates"""
    
    @staticmethod
    def create_idempotency_table(engine, table_name):
        """
        Create an idempotency tracking table if it doesn't exist.
        
        Args:
            engine: SQLAlchemy engine
            table_name: Name of the table to track
        """
        try:
            # SQL query to create the idempotency tracking table
            # This table stores the processing state for each pipeline run
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS pipeline_idempotency (
                id SERIAL PRIMARY KEY,                    -- Unique identifier for each tracking record
                table_name VARCHAR(255),                  -- Name of the table being processed
                last_processed_id VARCHAR(255),           -- Last successfully processed record ID
                last_processed_timestamp TIMESTAMP,       -- When the last record was processed
                batch_size INTEGER,                       -- Size of the last processed batch
                status VARCHAR(50),                       -- Processing status (completed/failed)
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP  -- When this tracking record was created
            )
            """
            
            # Execute the table creation query
            with engine.connect() as connection:
                connection.execute(text(create_table_query))
                connection.commit()  # Commit the transaction
                
            logger.info(f"Created idempotency tracking table for {table_name}")
            
        except Exception as e:
            logger.error(f"Error creating idempotency table: {str(e)}")
            raise

    @staticmethod
    def get_last_processed_id(engine, table_name):
        """
        Get the last processed ID for a table.
        
        Args:
            engine: SQLAlchemy engine
            table_name: Name of the table to check
            
        Returns:
            str: Last processed ID or None if no records
        """
        try:
            # Query to get the most recent processing record for the table
            # ORDER BY created_at DESC ensures we get the latest record
            query = text("""
                SELECT last_processed_id 
                FROM pipeline_idempotency 
                WHERE table_name = :table_name 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            
            with engine.connect() as connection:
                result = connection.execute(query, {"table_name": table_name}).fetchone()
                return result[0] if result else None  # Return None if no records found
                
        except Exception as e:
            logger.error(f"Error getting last processed ID: {str(e)}")
            raise

    @staticmethod
    def update_processing_status(engine, table_name, last_id, batch_size, status='completed'):
        """
        Update the processing status for a table.
        
        Args:
            engine: SQLAlchemy engine
            table_name: Name of the table being processed
            last_id: Last processed ID
            batch_size: Size of the processed batch
            status: Processing status
        """
        try:
            # Insert a new record to track the processing status
            # This creates an audit trail of all pipeline runs
            query = text("""
                INSERT INTO pipeline_idempotency 
                (table_name, last_processed_id, last_processed_timestamp, batch_size, status)
                VALUES (:table_name, :last_id, :timestamp, :batch_size, :status)
            """)
            
            with engine.connect() as connection:
                connection.execute(
                    query,
                    {
                        "table_name": table_name,
                        "last_id": last_id,
                        "timestamp": datetime.now(),  # Current timestamp for tracking
                        "batch_size": batch_size,
                        "status": status
                    }
                )
                connection.commit()  # Commit the transaction
                
            logger.info(f"Updated processing status for {table_name}")
            
        except Exception as e:
            logger.error(f"Error updating processing status: {str(e)}")
            raise

    @staticmethod
    def process_in_batches(engine, table_name, id_column, batch_size=1000):
        """
        Process data in batches with idempotency.
        
        Args:
            engine: SQLAlchemy engine
            table_name: Name of the table to process
            id_column: Name of the ID column
            batch_size: Size of each batch
            
        Yields:
            tuple: (batch_data, last_id)
        """
        try:
            # Get the last successfully processed ID
            # This ensures we don't reprocess already processed records
            last_processed_id = IdempotencyHandler.get_last_processed_id(engine, table_name)
            
            while True:
                # Build query based on whether we have a last processed ID
                # This is the key to idempotency - we only process records after the last processed ID
                if last_processed_id:
                    query = text(f"""
                        SELECT * FROM {table_name}
                        WHERE {id_column} > :last_id  -- Only get records after last processed ID
                        ORDER BY {id_column}          -- Ensure consistent ordering
                        LIMIT :batch_size            -- Process in manageable chunks
                    """)
                    params = {"last_id": last_processed_id, "batch_size": batch_size}
                else:
                    # If no last processed ID, start from the beginning
                    query = text(f"""
                        SELECT * FROM {table_name}
                        ORDER BY {id_column}
                        LIMIT :batch_size
                    """)
                    params = {"batch_size": batch_size}
                
                # Execute the query and get the batch
                with engine.connect() as connection:
                    result = connection.execute(query, params)
                    batch = result.fetchall()
                    
                    if not batch:
                        break  # No more records to process
                        
                    # Get the last ID in this batch for tracking
                    last_id = batch[-1][id_column]
                    yield batch, last_id  # Yield the batch and its last ID
                    
                    # Update the processing status after each successful batch
                    IdempotencyHandler.update_processing_status(
                        engine, 
                        table_name, 
                        last_id, 
                        len(batch)
                    )
                    
                    # Update the last processed ID for the next iteration
                    last_processed_id = last_id
                    
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            raise 