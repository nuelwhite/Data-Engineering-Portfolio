import pandas as pd
import os
import logging
from datetime import datetime 
import time
from tqdm import tqdm
import psutil

# Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.FileHandler('logs/processing.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# Get Memory Usage
def get_memory_usage():
    return psutil.Process(os.getpid()).memory_info().rss / (1024 ** 2)

# create a function to parse the date column
def parse_date(value):
    for fmt in ("%Y/%m/%d", "%/m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return pd.NaT


# Transform Chunk
def transform_chunk(df):
    try:
        # Drop nulls in purchase_amount
        df = df.dropna(subset=['purchase_amount'])

        # Convert customer_id to String type
        df.loc[:, 'customer_id'] = df['customer_id'].astype('Int32').astype('string')

        # convert transaction_id to String type
        df.loc[:, 'transaction_id'] = df['transaction_id'].astype('string')

        # Convert purchase_amount to float 
        df.loc[:, 'purchase_amount'] = df['purchase_amount'].astype('float32')

        # Standardize currency (preserve NaNs) and convert datatype to category
        df.loc[:, 'currency'] = df['currency'].apply(lambda x: 'USD' if str(x).upper() == 'USD' else x).astype('category')

        # Standardize date column
        # Clean purchase_date column before type conversion
        df.loc[:, 'purchase_date'] = df['purchase_date'].str.strip().str.replace('.','/').str.replace('-', '/')

        # parse the date column
        df.loc[:, 'purchase_date'] = df['purchase_date'].astype(str).apply(parse_date)

        # Standardize product_category column
        df.loc[:, 'product_category'] = df['product_category'].str.strip().str.lower()
        df.loc[:, 'product_category'] = df['product_category'].replace({
            'books': 'Books',
            'toys': 'Toys',
            'electronics': 'Electronics'
        }).astype('category')

        # Standardize is_returned and convert datatype to boolean
        df.loc[:, 'is_returned'] = df['is_returned'].astype(str).str.strip().str.lower()
        df.loc[:, 'is_returned'] = df['is_returned'].map({
            'yes': True, 'true': True,
            'no': False, 'false': False
        })
        df.loc[:, 'is_returned'] = df['is_returned'].astype('boolean')
        return df
    except Exception as e:
        logger.error(f"Error in transform_chunk: {e}")
        return pd.DataFrame()  # Return empty DataFrame on error


# Extract Chunk
def extract_chunk(reader):
    try:
        return next(reader)
    except StopIteration:
        return None


# Save Chunk
def save_chunk(df, path):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            df.to_csv(path, mode='w', index=False)
        else:
            df.to_csv(path, mode='a', header=False, index=False)
    except Exception as e:
        logger.error(f"Error saving chunk to {path}: {e}")


# Process CSV in Chunks
def process_csv_in_chunks(input_path, output_path, chunk_size=100000):
    try:
        start_time = time.time()
        logger.info("Starting chunked processing...")
        reader = pd.read_csv(input_path, chunksize=chunk_size)

        for i, chunk in enumerate(tqdm(reader, desc="Processing chunks")):
            logger.info(f"Chunk {i + 1}: Original shape = {chunk.shape}")
            mem_before = get_memory_usage()

            transformed = transform_chunk(chunk)

            mem_after = get_memory_usage()
            logger.info(
                f"Chunk {i + 1} processed. Rows: {len(transformed)} | "
                f"Memory Before: {mem_before:.2f} MB, After: {mem_after:.2f} MB, "
                f"Delta: {mem_after - mem_before:.2f} MB"
            )

            save_chunk(transformed, output_path)

        end_time = time.time()
        total_time = end_time - start_time
        logger.info(f"Finished processing all chunks. Total time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    except Exception as e:
        logger.error(f"Error in process_csv_in_chunks: {e}")



if __name__ == "__main__":
    process_csv_in_chunks("data/raw/transactions.csv", "data/processed/transactions_cleaned.csv")
