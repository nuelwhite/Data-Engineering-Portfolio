import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) 
import logging
import requests
import json
import os
from utils import *
from configs.logger_config import setup_logger
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import datetime
from typing import Optional
from kpi_analysis import (
    calculate_basic_metrics,
    get_top_movies,
    get_genre_analysis,
    get_revenue_budget_correlation,
    get_rating_distribution
)

load_dotenv()

# Set up loggers for each ETL stage, each with its own log file
extraction_logger = setup_logger('extraction', 'extraction.log')  # Logs to logs/extraction.log
transformation_logger = setup_logger('transformation', 'transformation.log')  # Logs to logs/transformation.log
kpi_logger = setup_logger('kpi_analysis', 'kpi.log')  # Logs to logs/kpi.log

# Set up the main pipeline logger (logs to logs/main_pipeline.log)
main_logger = setup_logger(logger_name='main', log_file_name='main_pipeline.log')

## Extract

def extract():
    extraction_logger.info("Starting extraction...")  # Log the start of extraction (stage log)
    main_logger.info("Starting extraction stage...")  # Log to main pipeline log

    # API parameters
    url = "https://api.themoviedb.org/3/movie"
    api_key = os.getenv('TMDB_API_KEY')  
    movie_ids = [0, 299534, 19995, 140607, 299536, 597, 135397, 420818, 24428, 168259, 99861,
                  284054, 12445, 181808, 330457, 351286, 109445, 321612, 260513] 

    # Call the api_extract function to fetch movie data
    for movie_data in api_extract(url, api_key, movie_ids):
        extraction_logger.debug(f"Processed movie: {movie_data.get('title', 'Unknown Title')}") 
        main_logger.debug(f"Processed movie: {movie_data.get('title', 'Unknown Title')}")

    extraction_logger.info("Extraction completed.")  # Log the end of extraction (stage log)
    main_logger.info("Extraction stage completed.")  # Log to main pipeline log


def transform(date_str: Optional[str] = None) -> None:
    """
    Transform the raw movie data into a processed format.
    
    Args:
        date_str (Optional[str]): Date string for the input file. If None, uses current date.
        
    Raises:
        FileNotFoundError: If the input file doesn't exist
        ValueError: If there are issues with the data transformation
    """
    try:
        # Set up date string for file naming
        if date_str is None:
            date_str = datetime.datetime.now().strftime('%Y-%m-%d')
            
        transformation_logger.info("Starting transformation stage...")
        main_logger.info("Starting transformation stage...")
        
        # Read raw data
        input_file = f'./data/raw/raw_movie_data_{date_str}.jsonl'
        transformation_logger.info(f"Reading raw data from {input_file}")
        df_movie = read_raw_json_file(input_file)
        
        # Drop irrelevant columns
        columns_to_drop = [
            'adult', 'imdb_id', 'original_title', 'video', 
            'homepage', 'backdrop_path', 'origin_country'
        ]
        transformation_logger.info("Dropping irrelevant columns...")
        df_movie = drop_columns(df_movie, columns_to_drop)
        
        # Convert monetary values to millions USD
        transformation_logger.info("Converting monetary values to millions USD...")
        df_movie = convert_to_millions(df_movie, ['budget', 'revenue'])
        
        # Convert datetime columns
        transformation_logger.info("Converting datetime columns...")
        df_movie = convert_datetime(df_movie, ['release_date'])
        
        # Round numeric columns
        transformation_logger.info("Rounding numeric columns...")
        df_movie = round_to_two(df_movie, ['vote_average', 'popularity'])
        
        # Explicitly extract nested fields with correct parameters
        transformation_logger.info("Extracting genres...")
        df_movie['genres'] = df_movie.apply(lambda row: extract_from_column(row, 'genres', key_name='name', is_list=True), axis=1)
        
        transformation_logger.info("Extracting production_companies...")
        df_movie['production_companies'] = df_movie.apply(lambda row: extract_from_column(row, 'production_companies', key_name='name', is_list=True), axis=1)
        
        transformation_logger.info("Extracting production_countries...")
        df_movie['production_countries'] = df_movie.apply(lambda row: extract_from_column(row, 'production_countries', key_name='name', is_list=True), axis=1)
        
        transformation_logger.info("Extracting spoken_languages...")
        df_movie['spoken_languages'] = df_movie.apply(lambda row: extract_from_column(row, 'spoken_languages', key_name='english_name', is_list=True), axis=1)
        
        # Extract franchise information (single dictionary)
        transformation_logger.info("Extracting franchise information...")
        df_movie['franchise'] = df_movie.apply(
            lambda row: extract_from_column(row, 'belongs_to_collection', key_name='name', is_list=False) or 'Standalone', 
            axis=1
        )
        
        # Extract credits information (handled separately)
        transformation_logger.info("Extracting credits information...")
        credits_info = df_movie.apply(extract_credits, axis=1)
        df_movie = pd.concat([df_movie, credits_info], axis=1)
        
        # Drop the original credits column
        df_movie = drop_columns(df_movie, ['credits'])
        
        # Reorder columns
        transformation_logger.info("Reordering columns...")
        column_order = [
            'id', 'title', 'tagline', 'release_date', 'genres', 'franchise',
            'original_language', 'budget_million_usd', 'revenue_million_usd', 
            'production_companies', 'production_countries', 'vote_count', 
            'vote_average', 'popularity', 'runtime', 'overview', 
            'spoken_languages', 'cast', 'cast_size', 'directors', 'crew_size'
        ]
        df_movie = reorder_columns(df_movie, column_order)
        
        # Save processed data
        transformation_logger.info("Saving processed data...")
        output_path = save_processed_data(df_movie, date_str=date_str)
        
        transformation_logger.info(f"Transformation completed successfully. Output saved to {output_path}")
        main_logger.info("Transformation stage completed successfully.")
        
    except FileNotFoundError as e:
        error_msg = f"Input file not found: {e}"
        transformation_logger.error(error_msg)
        main_logger.error(error_msg)
        raise
    except ValueError as e:
        error_msg = f"Data validation error: {e}"
        transformation_logger.error(error_msg)
        main_logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Unexpected error during transformation: {e}"
        transformation_logger.error(error_msg)
        main_logger.error(error_msg)
        raise

def analyze_kpi(date_str: Optional[str] = None) -> None:
    """
    Run KPI analysis on the processed movie data.
    
    Args:
        date_str (Optional[str]): Date string for the input file. If None, uses current date.
        
    Raises:
        FileNotFoundError: If the processed data file doesn't exist
        ValueError: If there are issues with the KPI analysis
    """
    try:
        # Set up date string for file naming
        if date_str is None:
            date_str = datetime.datetime.now().strftime('%Y-%m-%d')
            
        kpi_logger.info("Starting KPI analysis stage...")
        main_logger.info("Starting KPI analysis stage...")
        
        # Read processed data
        input_file = f'./data/processed/processed_data_{date_str}.csv'
        kpi_logger.info(f"Reading processed data from {input_file}")
        
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Processed data file not found: {input_file}")
            
        df = pd.read_csv(input_file)
        
        # Calculate and log basic metrics
        metrics = calculate_basic_metrics(df)
        kpi_logger.info(f"Calculated basic metrics: {metrics}")
        
        # Generate and save KPI visualizations
        kpi_logger.info("Generating KPI visualizations...")
        
        # Revenue vs Budget correlation
        correlation, revenue_budget_fig = get_revenue_budget_correlation(df)
        kpi_logger.info(f"Revenue-Budget correlation: {correlation:.2f}")
        
        # Rating distribution
        rating_dist_fig = get_rating_distribution(df)
        
        # Genre analysis
        genre_analysis = get_genre_analysis(df)
        kpi_logger.info("Completed genre analysis")
        
        # Save visualizations
        output_dir = f'./data/kpi_analysis_{date_str}'
        os.makedirs(output_dir, exist_ok=True)
        
        revenue_budget_fig.write_html(f'{output_dir}/revenue_budget_correlation.html')
        rating_dist_fig.write_html(f'{output_dir}/rating_distribution.html')
        
        # Save genre analysis to CSV
        genre_analysis.to_csv(f'{output_dir}/genre_analysis.csv', index=False)
        
        kpi_logger.info(f"KPI analysis completed. Results saved to {output_dir}")
        main_logger.info("KPI analysis stage completed successfully.")
        
    except FileNotFoundError as e:
        error_msg = f"Input file not found: {e}"
        kpi_logger.error(error_msg)
        main_logger.error(error_msg)
        raise
    except ValueError as e:
        error_msg = f"Data validation error: {e}"
        kpi_logger.error(error_msg)
        main_logger.error(error_msg)
        raise
    except Exception as e:
        error_msg = f"Unexpected error during KPI analysis: {e}"
        kpi_logger.error(error_msg)
        main_logger.error(error_msg)
        raise

# In your main ETL flow
if __name__ == '__main__':
    extract()  # Run the extraction step
    transform()  # Run the transformation step
    analyze_kpi()  # Run the KPI analysis step






