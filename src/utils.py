import requests
import json
import logging
import pandas as pd
import numpy as np
import os
import datetime


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
        today = datetime.today().strftime('%Y-%m-%d')
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

                # Yield the movie data for streaming/processing
                yield movie_data

            except requests.exceptions.Timeout as time_out:
                logging.error(f'Timeout for fetching movie ID {movie_id} : {time_out}')
                raise TimeoutError('Timeout Error: Exhausted timeout.')
            except requests.exceptions.HTTPError as http_error:
                logging.error(f'HTTP Error for movie ID {movie_id} : {http_error}')
                raise ConnectionError(f'HTTP Error for movie ID {movie_id}: {http_error}')
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
