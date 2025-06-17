import logging
import json
import os
from datetime import datetime
from pathlib import Path

# Initialize logger for tracking pipeline operations
logger = logging.getLogger(__name__)

class IdempotencyHandler:
    """Handles idempotency in data pipelines using file-based tracking"""
    
    def __init__(self, tracking_dir='tracking'):
        """
        Initialize the idempotency handler.
        
        Args:
            tracking_dir: Directory to store tracking files
        """
        # Create tracking directory if it doesn't exist
        self.tracking_dir = Path(tracking_dir)
        self.tracking_dir.mkdir(parents=True, exist_ok=True)
        
    def get_tracking_file(self, table_name):
        """Get the path to the tracking file for a table"""
        return self.tracking_dir / f"{table_name}_tracking.json"
    
    def get_last_processed_id(self, table_name):
        """
        Get the last processed ID for a table from the tracking file.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            str: Last processed ID or None if no records
        """
        try:
            tracking_file = self.get_tracking_file(table_name)
            
            if not tracking_file.exists():
                return None
                
            with open(tracking_file, 'r') as f:
                tracking_data = json.load(f)
                return tracking_data.get('last_processed_id')
                
        except Exception as e:
            logger.error(f"Error reading tracking file: {str(e)}")
            return None
    
    def update_processing_status(self, table_name, last_id, batch_size, status='completed'):
        """
        Update the processing status in the tracking file.
        
        Args:
            table_name: Name of the table being processed
            last_id: Last processed ID
            batch_size: Size of the processed batch
            status: Processing status
        """
        try:
            tracking_file = self.get_tracking_file(table_name)
            
            # Create or update tracking data
            tracking_data = {
                'table_name': table_name,
                'last_processed_id': last_id,
                'last_processed_timestamp': datetime.now().isoformat(),
                'batch_size': batch_size,
                'status': status
            }
            
            # Write to tracking file
            with open(tracking_file, 'w') as f:
                json.dump(tracking_data, f, indent=2)
                
            logger.info(f"Updated processing status for {table_name}")
            
        except Exception as e:
            logger.error(f"Error updating tracking file: {str(e)}")
            raise
    
    def process_in_batches(self, engine, table_name, id_column, batch_size=1000):
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
            last_processed_id = self.get_last_processed_id(table_name)
            
            while True:
                # Build query based on whether we have a last processed ID
                if last_processed_id:
                    query = f"""
                        SELECT * FROM {table_name}
                        WHERE {id_column} > :last_id  -- Only get records after last processed ID
                        ORDER BY {id_column}          -- Ensure consistent ordering
                        LIMIT :batch_size            -- Process in manageable chunks
                    """
                    params = {"last_id": last_processed_id, "batch_size": batch_size}
                else:
                    # If no last processed ID, start from the beginning
                    query = f"""
                        SELECT * FROM {table_name}
                        ORDER BY {id_column}
                        LIMIT :batch_size
                    """
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
                    self.update_processing_status(
                        table_name, 
                        last_id, 
                        len(batch)
                    )
                    
                    # Update the last processed ID for the next iteration
                    last_processed_id = last_id
                    
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            raise 