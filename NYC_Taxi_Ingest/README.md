# NYC Taxi Data Ingestion Project

## Project Overview
This project demonstrates an end-to-end data ingestion pipeline for the NYC Taxi dataset. The goal is to automate the process of downloading, transforming, and ingesting large datasets into a Postgres database for analysis and visualization. 

## Technologies Used
- **Programming Languages**: Python (pandas, argparse, SQLAlchemy)
- **Database**: PostgreSQL
- **Tools**: Docker, Docker Compose, pgAdmin
- **Libraries**: pandas, SQLAlchemy, psycopg2

## Workflow
1. **Data Source**  
   - The dataset is sourced from the NYC Taxi and Limousine Commission.
   - Data format: Parquet files, converted to CSV for ingestion.

2. **Pipeline Steps**  
   - **Download**: Retrieve the NYC Taxi dataset for January 2021.  
   - **Transform**: Convert Parquet files to CSV and correct schema inconsistencies (e.g., changing date-related columns from TEXT to TIMESTAMP).  
   - **Ingest**: Use Python scripts to batch load the CSV data into a Postgres database in increments of 100,000 rows.

3. **Database Schema**  
   - A table named `yellow_taxi_data` was created in Postgres with the following schema:  
     ```sql
     CREATE TABLE "yellow_tripdata_2021-01.csv" (
     VendorID" BIGINT,
     tpep_pickup_datetime TIMESTAMP WITHOUT TIME ZONE,
     tpep_dropoff_datetime TIMESTAMP WITHOUT TIME ZONE,
     passenger_count FLOAT(53), 
     trip_distance FLOAT(53), 
	  "RatecodeID" FLOAT(53), 
	  store_and_fwd_flag TEXT, 
	  "PULocationID" BIGINT, 
	  "DOLocationID" BIGINT, 
	  payment_type BIGINT, 
	  fare_amount FLOAT(53), 
	  extra FLOAT(53), 
	  mta_tax FLOAT(53), 
	  tip_amount FLOAT(53), 
	  tolls_amount FLOAT(53), 
	  improvement_surcharge FLOAT(53), 
	  total_amount FLOAT(53), 
	  congestion_surcharge FLOAT(53), 
	  airport_fee FLOAT(53)
      )
     ```

4. **Automation with Docker**  
   - Dockerized the Python ingestion script.
   - Used Docker Compose to connect Postgres, pgAdmin, and the ingestion script in a seamless environment.

5. **Visualization**  
   - Connected pgAdmin to the Postgres database for querying and visualizing data insights.

## Challenges and Solutions
- **Challenge**: Schema mismatch in the dataset (TEXT instead of TIMESTAMP for datetime columns).  
  **Solution**: Added a transformation step to parse and format the datetime columns correctly before ingestion.

- **Challenge**: Large dataset causing memory issues during ingestion.  
  **Solution**: Used batching with pandas iterators to process data in chunks of 100,000 rows.

## Results
- Successfully ingested over 1 million rows of NYC Taxi data into Postgres.
- Verified data integrity and schema accuracy through SQL queries.
- Built a reusable pipeline for future data ingestion tasks.

## Future Improvements
- Integrate Spark for handling larger datasets.
- Add automated tests for data validation.
- Extend pipeline to include data cleaning and aggregation steps.
