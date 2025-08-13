# Online Retail ETL Pipeline

A comprehensive ETL (Extract, Transform, Load) pipeline for analyzing online retail transaction data using PySpark RDDs. 

Data Source: https://www.kaggle.com/datasets/thedevastator/online-retail-transaction-records


## Overview

This project was developed as a hands-on exercise to solidify my understanding of fundamental PySpark concepts. The key objectives were to:

* Reinforce proficiency with RDDs as the foundational distributed data processing primitive.

* Move beyond theoretical knowledge by applying RDD-based techniques to a real-world dataset.

* Build a tangible demonstration of core PySpark principles as a solid foundation for exploring higher-level APIs.

This pipeline processes online retail transaction data to provide insights into:
- Sales performance and revenue metrics
- Product popularity and performance
- Customer behavior and spending patterns
- Time-based sales trends
- Geographic distribution of sales


## Key Features of the ETL Pipeline:

**Extract (E)**

- Reads CSV data with proper schema inference
- Converts to PySpark RDD for distributed processing
- Handles large datasets efficiently

**Transform (T)**

- Cleans missing CustomerID values
- Parses date fields for time analysis
- Converts data types as needed
- Prepare data for data analysis

**Load (L)**

- Generates comprehensive analysis reports
- Saves results to files
- Provides console output with key metrics


### 4. Analysis Modules
- **Sales Overview**: Total transactions, revenue, average order value
- **Product Analysis**: Top products by quantity and revenue
- **Customer Analysis**: Spending patterns, frequency, average order values


### 5. Report Generation
- Creates comprehensive text report
- Saves results to file
- Provides summary statistics

## Output Files

- `retail_analysis_report.txt`: Comprehensive analysis report
- `etl_pipeline.log`: Pipeline execution logs
- Console output with summary statistics


## Data Schema

The pipeline expects CSV data with the following columns:
- `InvoiceNo`: Transaction identifier
- `StockCode`: Product code
- `Description`: Product description
- `Quantity`: Units sold
- `InvoiceDate`: Transaction date/time
- `UnitPrice`: Price per unit
- `CustomerID`: Customer identifier
- `Country`: Customer country


## Error Handling

- Comprehensive exception handling
- Detailed logging at all stages
- Graceful failure with informative error messages


## Portfolio Benefits

This project demonstrates:
- **PySpark RDD Operations**: Map, reduce, filter, and aggregation
- **ETL Pipeline Design**: Extract, transform, load patterns
- **Data Quality Management**: Handling missing values and data cleaning
- **Business Intelligence**: Sales analytics and customer insights
- **Code Organization**: Clean, modular, and maintainable code
- **Error Handling**: Production-quality error management
- **Logging**: Professional logging practices

## Troubleshooting


### Logs

Check `etl_pipeline.log` for detailed execution information and error details.

