import requests
import json
import logging
import pandas as pd
import numpy as np
import os
import datetime
import ast
from typing import List, Union, Dict, Any, Optional



def api_extract(url, api_key, movie_ids, save_to_file=True, file_path='./data/raw/raw_movie_data.jsonl'):
    """
    Fetch movie data from an API for a list of movie IDs, streaming results and optionally saving to a .jsonl file.

    Args:
        url (str): Base URL for the API endpoint.
        api_key (str): API key for authentication.
        movie_ids (list): List of movie IDs to fetch.
        save_to_file (bool): Whether to save each movie's data to a file as it is fetched. Default is True.
        file_path (str): Path to the output .jsonl file. Default is './data/raw/raw_movie_data.jsonl'.

    Yields:
        dict: Movie data for each movie ID.
    """
    # Raise an error if no API key is provided
    if not api_key:
        raise ValueError('API Key is required.')

    if save_to_file and file_path == './data/raw/raw_movie_data.jsonl':
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        file_path = f'./data/raw/raw_movie_data_{today}.jsonl'

    file_handle = None
    if save_to_file:
        # Ensure the output directory exists and open the file for writing
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file_handle = open(file_path, 'w', encoding='utf-8')

    try:
        for movie_id in movie_ids:
            try:
                # Make the API request for the current movie ID
                response = requests.get(f'{url}/{movie_id}?api_key={api_key}&append_to_response=credits', timeout=10)
                response.raise_for_status()
                movie_data = response.json()

                if not movie_data:
                    raise RuntimeError(f'Empty response for movie ID {movie_id}.')

                logging.info(f'Fetched movie ID {movie_id} successfully.')

                # Write each movie's data as a line in the .jsonl file (if enabled)
                if file_handle:
                    file_handle.write(json.dumps(movie_data) + '\n')
                    logging.info(f'Movie ID {movie_id} written to file successfully.')

                # Yield the movie data for streaming/processing
                yield movie_data

            except requests.exceptions.Timeout as time_out:
                logging.error(f'Timeout for fetching movie ID {movie_id} : {time_out}')
                raise TimeoutError('Timeout Error: Exhausted timeout.')
            except requests.exceptions.HTTPError as http_error:
                logging.error(f'HTTP Error for movie ID {movie_id} : {http_error}')
                logging.info(f'Failed to fetch movie ID {movie_id}. Skipping.')
                continue
            except requests.exceptions.ConnectionError as conn_error:
                logging.error(f'Connection Error: Cannot connect... {conn_error}')
                raise ConnectionError(f'Connection Error: Cannot connect... {conn_error}')
            except requests.exceptions.RequestException as e:
                logging.error(f'Request error for movie ID {movie_id}: {e}')
                raise ConnectionError(f'Request error: Could not request movie ID {movie_id}')
            except Exception as e:
                logging.error(f'An error occurred for movie ID {movie_id}: {e}')
                raise RuntimeError(f'An error {e} occurred.')
    finally:
        # Ensure the file is properly closed after processing
        if file_handle:
            file_handle.close()
            # Log if the file was created successfully
            if os.path.exists(file_path):
                logging.info(f'File created successfully: {file_path}')
            else:
                logging.error(f'File was not created: {file_path}')


def read_raw_json_file(file_path: str) -> pd.DataFrame:
    """
    Read JSONL data from a file into a pandas DataFrame, preserving JSON structures.
    
    Args:
        file_path (str): Path to the JSONL file
        
    Returns:
        pd.DataFrame: DataFrame containing the JSONL data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file is not valid JSONL
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Read JSONL file line by line
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    # Parse each line as JSON
                    movie_data = json.loads(line.strip())
                    
                    # Convert nested structures to strings to preserve them
                    for key in ['genres', 'production_companies', 'production_countries', 'spoken_languages']:
                        if key in movie_data:
                            movie_data[key] = json.dumps(movie_data[key])
                            
                    data.append(movie_data)
                except json.JSONDecodeError as e:
                    logging.warning(f"Error decoding JSON line: {e}")
                    continue
        
        if not data:
            raise ValueError("No valid JSON data found in file")
            
        df_movies = pd.DataFrame(data)
        logging.info(f"Successfully read JSONL file: {file_path}")
        return df_movies
        
    except Exception as e:
        logging.error(f"Error reading JSONL file {file_path}: {e}")
        raise

def drop_columns(df: pd.DataFrame, cols_to_drop: List[str]) -> pd.DataFrame:
    """
    Remove specified columns from a DataFrame.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        cols_to_drop (List[str]): List of column names to drop
        
    Returns:
        pd.DataFrame: DataFrame with specified columns removed
        
    Raises:
        KeyError: If any specified column doesn't exist
    """
    try:
        # Validate columns exist
        missing_cols = [col for col in cols_to_drop if col not in df.columns]
        if missing_cols:
            raise KeyError(f"Columns not found in DataFrame: {missing_cols}")
            
        df = df.drop(columns=cols_to_drop)
        logging.info(f"Successfully dropped columns: {cols_to_drop}")
        return df
        
    except Exception as e:
        logging.error(f"Error dropping columns: {e}")
        raise

def convert_to_millions(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """
    Convert specified columns to millions USD.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        cols (List[str]): List of column names to convert
        
    Returns:
        pd.DataFrame: DataFrame with converted columns
        
    Raises:
        ValueError: If any column is not numeric
    """
    try:
        for col in cols:
            if col not in df.columns:
                logging.warning(f"Column {col} not found, skipping")
                continue
                
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError(f"Column {col} is not numeric")
                
            new_col = f'{col}_million_usd'
            df[new_col] = (df[col]/1e6).round(2)
            logging.info(f"Converted {col} to millions USD")
            
        return df
        
    except Exception as e:
        logging.error(f"Error converting to millions: {e}")
        raise

def convert_datetime(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """
    Convert specified columns to datetime format.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        cols (List[str]): List of column names to convert
        
    Returns:
        pd.DataFrame: DataFrame with converted datetime columns
    """
    try:
        for col in cols:
            if col not in df.columns:
                logging.warning(f"Column {col} not found, skipping")
                continue
                
            df[col] = pd.to_datetime(df[col], errors='coerce')
            invalid_dates = df[col].isna().sum()
            if invalid_dates > 0:
                logging.warning(f"Found {invalid_dates} invalid dates in column {col}")
                
        return df
        
    except Exception as e:
        logging.error(f"Error converting to datetime: {e}")
        raise

def round_to_two(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    """
    Round specified columns to 2 decimal places.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        cols (List[str]): List of column names to round
        
    Returns:
        pd.DataFrame: DataFrame with rounded columns
        
    Raises:
        ValueError: If any column is not numeric
    """
    try:
        for col in cols:
            if col not in df.columns:
                logging.warning(f"Column {col} not found, skipping")
                continue
                
            if not pd.api.types.is_numeric_dtype(df[col]):
                raise ValueError(f"Column {col} is not numeric")
                
            df[col] = df[col].round(2)
            logging.info(f"Rounded {col} to 2 decimal places")
            
        return df
        
    except Exception as e:
        logging.error(f"Error rounding columns: {e}")
        raise

def reorder_columns(df: pd.DataFrame, order_of_columns: List[str]) -> pd.DataFrame:
    """
    Reorder DataFrame columns and reset index.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        order_of_columns (List[str]): List of column names in desired order
        
    Returns:
        pd.DataFrame: DataFrame with reordered columns
        
    Raises:
        KeyError: If any specified column doesn't exist
    """
    try:
        # Validate all columns exist
        missing_cols = [col for col in order_of_columns if col not in df.columns]
        if missing_cols:
            raise KeyError(f"Columns not found in DataFrame: {missing_cols}")
            
        df = df[order_of_columns]
        df = df.reset_index(drop=True)
        logging.info("Successfully reordered columns and reset index")
        return df
        
    except Exception as e:
        logging.error(f"Error reordering columns: {e}")
        raise

def save_processed_data(df: pd.DataFrame, 
                       file_path: str = './data/processed/',
                       date_str: Optional[str] = None) -> str:
    """
    Save processed DataFrame to CSV with date stamp.
    
    Args:
        df (pd.DataFrame): DataFrame to save
        file_path (str): Directory path to save the file
        date_str (Optional[str]): Date string for filename. If None, uses current date
        
    Returns:
        str: Path to the saved file
        
    Raises:
        OSError: If there are issues creating directory or writing file
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(file_path, exist_ok=True)
        
        # Generate date string if not provided
        if date_str is None:
            date_str = datetime.datetime.now().strftime('%Y-%m-%d')
            
        output_path = f'{file_path}/processed_data_{date_str}.csv'
        df.to_csv(output_path, index=False)
        logging.info(f"Successfully saved processed data to: {output_path}")
        return output_path
        
    except Exception as e:
        logging.error(f"Error saving processed data: {e}")
        raise

def extract_from_column(row: pd.Series, 
                       column_name: str, 
                       key_name: str = 'name', 
                       is_list: bool = False, 
                       separator: str = '|') -> Optional[str]:
    """
    Extract data from nested JSON columns, handling both stringified and already-parsed data.
    
    Args:
        row (pd.Series): Row containing the nested data
        column_name (str): Name of the column containing nested data
        key_name (str): Key to extract from dictionaries
        is_list (bool): Whether the data is a list of dictionaries
        separator (str): Separator to use when joining list values
        
    Returns:
        Optional[str]: Extracted data or None if extraction fails
    """
    try:
        value = row[column_name]
        logging.info(f"Processing {column_name} with value type: {type(value)}")
        
        if pd.isna(value):
            logging.info(f"Value is NA for {column_name}")
            return None
            
        # If value is a string, try to parse it
        if isinstance(value, str):
            logging.info(f"Attempting to parse string value for {column_name}")
            try:
                # First try json.loads
                parsed = json.loads(value)
                logging.info(f"Successfully parsed JSON for {column_name}")
            except json.JSONDecodeError:
                try:
                    # If json.loads fails, try ast.literal_eval
                    parsed = ast.literal_eval(value)
                    logging.info(f"Successfully parsed with ast.literal_eval for {column_name}")
                except (ValueError, SyntaxError) as e:
                    logging.warning(f"Could not parse string value in column {column_name}: {e}")
                    return None
        else:
            parsed = value
            logging.info(f"Using non-string value for {column_name} of type {type(parsed)}")
            
        # Handle list of dictionaries (for genres, production_companies, etc.)
        if is_list:
            # Convert numpy array to list if necessary
            if isinstance(parsed, np.ndarray):
                parsed = parsed.tolist()
                
            if not isinstance(parsed, list):
                logging.warning(f"Expected list in column {column_name}, got {type(parsed)}")
                return None
                
            logging.info(f"Processing list of length {len(parsed)} for {column_name}")
            values = []
            for item in parsed:
                if isinstance(item, dict) and key_name in item:
                    values.append(str(item[key_name]))
            result = separator.join(values) if values else None
            logging.info(f"Extracted values for {column_name}: {result}")
            return result
            
        # Handle single dictionary (for belongs_to_collection, etc.)
        elif isinstance(parsed, dict):
            if key_name in parsed:
                result = str(parsed[key_name])
                logging.info(f"Extracted value for {column_name}: {result}")
                return result
            else:
                logging.warning(f"Key '{key_name}' not found in dictionary for {column_name}")
                return None
            
        logging.warning(f"No valid data found for {column_name}")
        return None
        
    except Exception as e:
        logging.error(f"Error extracting from column {column_name}: {str(e)}")
        return None

def extract_credits(row: pd.Series) -> pd.Series:
    """
    Extract cast and crew information from movie credits, handling both stringified and already-parsed data.
    
    Args:
        row (pd.Series): Row containing credits data
        
    Returns:
        pd.Series: Series containing cast_size, crew_size, directors, and cast
    """
    try:
        value = row['credits']
        if pd.isna(value):
            return pd.Series({
                'cast_size': 0,
                'crew_size': 0,
                'directors': "",
                'cast': ""
            })
            
        # If value is a string, try to parse it
        if isinstance(value, str):
            try:
                # First try json.loads
                credits_dict = json.loads(value)
            except json.JSONDecodeError:
                try:
                    # If json.loads fails, try ast.literal_eval
                    credits_dict = ast.literal_eval(value)
                except Exception:
                    logging.warning("Could not parse credits data")
                    return pd.Series({
                        'cast_size': 0,
                        'crew_size': 0,
                        'directors': "",
                        'cast': ""
                    })
        elif isinstance(value, dict):
            credits_dict = value
        else:
            return pd.Series({
                'cast_size': 0,
                'crew_size': 0,
                'directors': "",
                'cast': ""
            })
            
        # Get cast members (top 10 by order)
        cast = sorted(credits_dict.get('cast', []), 
                     key=lambda x: x.get('order', float('inf')) if isinstance(x, dict) else float('inf'))[:10]
        main_cast = "|".join([actor['name'] for actor in cast if isinstance(actor, dict) and actor.get('name')])
        
        # Get cast and crew sizes
        cast_size = len(credits_dict.get('cast', []))
        crew_size = len(credits_dict.get('crew', []))
        
        # Get directors
        crew = credits_dict.get('crew', [])
        directors = "|".join([member['name'] for member in crew 
                            if isinstance(member, dict) and member.get('job') == 'Director' and member.get('name')])
                            
        return pd.Series({
            'cast_size': cast_size,
            'crew_size': crew_size,
            'directors': directors,
            'cast': main_cast
        })
    except Exception as e:
        logging.error(f"Error extracting credits: {e}")
        return pd.Series({
            'cast_size': 0,
            'crew_size': 0,
            'directors': "",
            'cast': ""
        })



# until this line are functions for transformations
