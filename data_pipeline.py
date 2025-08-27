import requests
import os
import sys
from dotenv import load_dotenv
import datetime
import json
import logging

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat_ws, size, explode, collect_list, to_date, round

# start spark session
spark = SparkSession.builder.appName('TMDB_movie_project').getOrCreate()

# configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create file handler
file_handler = logging.FileHandler('pipeline_log.log')
file_handler.setLevel(logging.INFO)

# create stream handler for console printing 
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

# creater formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)




# api extraction function

def api_data_extraction(api_key, base_url, data_points):
    if not api_key:
        raise ValueError('API key is required!')
    results = []
    params = {
        'api_key': api_key,
        'append_to_response': 'credits'
    }

    for data_point in data_points:
        try:
            # Construct the full URL with the data point
            full_url = f'{base_url}/{data_point}' 
            response = requests.get(full_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Check for empty data, assuming an empty dictionary is an error
            if not data:
                logger.warning(f'Warning: Empty response for data point {data_point}. Skipping.')
                continue
                
            results.append(data)
            logger.debug(f'movie id {data_point} extracted successfully!')
        
        except requests.exceptions.HTTPError as http_error:
            # Log the specific error and continue to the next data point
            logger.warning(f'HTTP error for data point {data_point}: {http_error}')
            logger.warning(f'Response content: {http_error.response.text}')
            continue
        except requests.exceptions.Timeout as timeout_error:
            logger.warning(f"Timeout error for {data_point}: {timeout_error}")
            continue
        except requests.exceptions.ConnectionError as conn_error:
            logger.warning(f"Connection error for {data_point}: {conn_error}")
            continue
        except requests.exceptions.RequestException as req_error:
            logger.warning(f"An unexpected requests error occurred for {data_point}: {req_error}")
            continue
        except Exception as e:
            logger.critical(f"An unexpected error occurred for {data_point}: {e}")
            continue
    return results



# save the extracted data

def save_extracted_data(data, file_path):
    """Saves a list of data to a specified JSON file path."""

    directory = os.path.dirname(file_path)

    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
        except OSError as e:
            logger.warning(f"Error creating directory {directory}: {e}")
            return

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logger.debug(f"Successfully saved data to {file_path}")
    except IOError as e:
        logger.critical(f'Error saving data to JSON file: {e}')
    except Exception as e:
        logger.critical(f"An unexpected error occurred while saving: {e}")


def transform(data):
    # load data with rdd to keep json structs intact
    movies_rdd = spark.sparkContext.parallelize(data).map(lambda x: json.dumps(x))
    import requests
import os
import sys
from dotenv import load_dotenv
import datetime
import json
import logging

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# start spark session
spark = SparkSession.builder.appName('TMDB_movie_project').getOrCreate()

# configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create file handler
file_handler = logging.FileHandler('pipeline_log.log')
file_handler.setLevel(logging.INFO)

# create stream handler for console printing 
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

# creater formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)




# api extraction function

def api_data_extraction(api_key, base_url, data_points):
    if not api_key:
        raise ValueError('API key is required!')
    results = []
    params = {
        'api_key': api_key,
        'append_to_response': 'credits'
    }

    for data_point in data_points:
        try:
            # Construct the full URL with the data point
            full_url = f'{base_url}/{data_point}' 
            response = requests.get(full_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Check for empty data, assuming an empty dictionary is an error
            if not data:
                logger.warning(f'Warning: Empty response for data point {data_point}. Skipping.')
                continue
                
            results.append(data)
            logger.debug(f'movie id {data_point} extracted successfully!')
        
        except requests.exceptions.HTTPError as http_error:
            # Log the specific error and continue to the next data point
            logger.warning(f'HTTP error for data point {data_point}: {http_error}')
            logger.warning(f'Response content: {http_error.response.text}')
            continue
        except requests.exceptions.Timeout as timeout_error:
            logger.warning(f"Timeout error for {data_point}: {timeout_error}")
            continue
        except requests.exceptions.ConnectionError as conn_error:
            logger.warning(f"Connection error for {data_point}: {conn_error}")
            continue
        except requests.exceptions.RequestException as req_error:
            logger.warning(f"An unexpected requests error occurred for {data_point}: {req_error}")
            continue
        except Exception as e:
            logger.critical(f"An unexpected error occurred for {data_point}: {e}")
            continue
    return results



# save the extracted data

def save_extracted_data(data, file_path):
    """Saves a list of data to a specified JSON file path."""

    directory = os.path.dirname(file_path)

    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
        except OSError as e:
            logger.warning(f"Error creating directory {directory}: {e}")
            return

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logger.debug(f"Successfully saved data to {file_path}")
    except IOError as e:
        logger.critical(f'Error saving data to JSON file: {e}')
    except Exception as e:
        logger.critical(f"An unexpected error occurred while saving: {e}")


def transform(data):
    # load data with rdd to keep json structs intact
    movies_rdd = spark.sparkContext.parallelize(data).map(lambda x: json.dumps(x))
    import requests
import os
import sys
from dotenv import load_dotenv
import datetime
import json
import logging

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# start spark session
spark = SparkSession.builder.appName('TMDB_movie_project').getOrCreate()

# configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create file handler
file_handler = logging.FileHandler('pipeline_log.log')
file_handler.setLevel(logging.INFO)

# create stream handler for console printing 
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)

# creater formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)




# api extraction function

def api_data_extraction(api_key, base_url, data_points):
    if not api_key:
        raise ValueError('API key is required!')
    results = []
    params = {
        'api_key': api_key,
        'append_to_response': 'credits'
    }

    for data_point in data_points:
        try:
            # Construct the full URL with the data point
            full_url = f'{base_url}/{data_point}' 
            response = requests.get(full_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Check for empty data, assuming an empty dictionary is an error
            if not data:
                logger.warning(f'Warning: Empty response for data point {data_point}. Skipping.')
                continue
                
            results.append(data)
            logger.debug(f'movie id {data_point} extracted successfully!')
        
        except requests.exceptions.HTTPError as http_error:
            # Log the specific error and continue to the next data point
            logger.warning(f'HTTP error for data point {data_point}: {http_error}')
            logger.warning(f'Response content: {http_error.response.text}')
            continue
        except requests.exceptions.Timeout as timeout_error:
            logger.warning(f"Timeout error for {data_point}: {timeout_error}")
            continue
        except requests.exceptions.ConnectionError as conn_error:
            logger.warning(f"Connection error for {data_point}: {conn_error}")
            continue
        except requests.exceptions.RequestException as req_error:
            logger.warning(f"An unexpected requests error occurred for {data_point}: {req_error}")
            continue
        except Exception as e:
            logger.critical(f"An unexpected error occurred for {data_point}: {e}")
            continue
    return results



# save the extracted data

def save_extracted_data(data, file_path):
    """Saves a list of data to a specified JSON file path."""

    directory = os.path.dirname(file_path)

    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
        except OSError as e:
            logger.warning(f"Error creating directory {directory}: {e}")
            return

    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logger.debug(f"Successfully saved data to {file_path}")
    except IOError as e:
        logger.critical(f'Error saving data to JSON file: {e}')
    except Exception as e:
        logger.critical(f"An unexpected error occurred while saving: {e}")


def transform_movie_data(data):
    # load data with rdd to keep json structs intact
    movies_rdd = spark.sparkContext.parallelize(data).map(lambda x: json.dumps(x))
    # convert the rdd to a dataframe
    movie_data_df = spark.read.json(movies_rdd)

    '''Transformations'''
    # extract collection name from belongs_to_collection
    movie_data_df = movie_data_df.withColumn('belongs_to_collection', col("belongs_to_collection.name"))

    # extract genres from genres seperated by |
    movie_data_df = movie_data_df.withColumn('genres', concat_ws("|", col('genres.name')))

    # extract spoken languages from spoken_languages seperated by |
    movie_data_df = movie_data_df.withColumn( 'spoken_languages', concat_ws("|", col('spoken_languages.name')))

    # extract production companies from production_companies seperated by |
    movie_data_df = movie_data_df.withColumn('production_companies', concat_ws("|", col('production_companies.name')))

    # extract production countries from production_countries seperated by |
    movie_data_df = movie_data_df.withColumn('production_countries', concat_ws("|", col('production_countries.name')))

    # transform credits columns
    # create a new column for the cast
    movie_data_df = movie_data_df.withColumn('casts', concat_ws('|', col('credits.cast.name')))

    # create a new column for cast size
    movie_data_df = movie_data_df.withColumn('cast_size', size(col('credits.cast')))

    # create a new column for crew size
    movie_data_df = movie_data_df.withColumn('crew_size', size(col('credits.crew')))

    # create new directors dataframe and join it to the main df after
    directors_df = movie_data_df.withColumn("crew_member", 
    explode(col("credits.crew"))
    ).filter(col("crew_member.job") == "Director"
    ).groupBy("title"
    ).agg(
    concat_ws("|", collect_list(col("crew_member.name"))).alias("directors"))

    # join to main df
    movie_data_df = movie_data_df.join(directors_df, on='title', how='left')

    # drop credits
    movie_data_df = movie_data_df.drop('credits')

    # convert release_date to date type
    movie_data_df = movie_data_df.withColumn('release_date', to_date('release_date', 'yyyy-MM-dd'))

    # convert runtime dtype from long to int
    movie_data_df = movie_data_df.withColumn('runtime', col('runtime').cast('int'))

    movie_data_df = (movie_data_df.withColumn("revenue", round((col("revenue") / 1_000_000).cast("double"), 2))
                     .withColumn("budget", round((col("budget") / 1_000_000).cast("double"), 2))
                     .withColumnRenamed("revenue", "revenue_million_usd")
                     .withColumnRenamed("budget", "budget_million_usd"))
    
    # round vote_average to 1 decimal place
    movie_data_df = movie_data_df.withColumn('vote_average', round(col('vote_average'), 1))

    # round popularity to 2 decimal place
    movie_data_df = movie_data_df.withColumn('popularity', round(col('popularity'), 2))


    # reorder columns
    movie_data_df = movie_data_df.select('id', 'title', 'tagline', 'release_date', 'genres', 'belongs_to_collection',
    'original_language', 'budget_million_usd', 'revenue_million_usd', 'production_companies',
    'production_countries', 'vote_count', 'vote_average', 'popularity', 'runtime',
    'overview', 'spoken_languages', 'casts', 'cast_size', 'directors', 'crew_size')


    '''Advanced Feature Engineering - Analysis'''
    # revenues
    # highest revenues
    movie_data_df = movie_data_df.withColumn('profit', round(col('revenue_million_usd') - col('budget_million_usd'), 2))  

    # ROI - return on investment
    movie_data_df = movie_data_df.withColumn('roi', round(col('profit') / col('budget_million_usd'), 2))


    return movie_data_df

def save_processed_data(df, file_path):
    df.write.csv(file_path, header=True, mode="overwrite")
    logger.info(f"Successfully saved processed data to {file_path}")



if __name__ == "__main__":
    # load data
    logger.info("Starting the data pipeline...")

    # load environment variables from .env file
    load_dotenv()

    # load environment variable
    TMDB_API_KEY = os.getenv('TMDB_API_KEY')

    # set base url of TMDB website
    TMDB_BASE_URL = 'https://api.themoviedb.org/3/movie'

    # Data points to extract
    movie_ids = [0, 299534, 19995, 140607, 299536, 597, 135397, 420818, 24428, 168259, 99861,
                 284054, 12445, 181808, 330457, 351286, 109445, 321612, 260513]

    # extract data
    logger.info("Extracting data from the API...")  
    movie_data = api_data_extraction(TMDB_API_KEY, TMDB_BASE_URL, movie_ids)
    logger.info("Data extracted successfully!")

    # transform data
    logger.info("Transforming data...")
    movie_data_df = transform_movie_data(movie_data)
    logger.info("Data transformed successfully!")

    # save data
    logger.info("Saving data...")
    save_processed_data(movie_data_df, 'data/processed_movie_data.csv')
    logger.info("Data saved successfully!")

    logger.info("Data pipeline completed successfully!")
