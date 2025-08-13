import logging
import sys
from datetime import datetime
from typing import List, Tuple, Dict, Any
from pyspark.sql import SparkSession, Row
from pyspark.rdd import RDD

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('etl_pipeline.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class RetailETLPipeline:
    """Main ETL pipeline class for retail data processing."""
    
    def __init__(self, app_name):
        """Initialize the ETL pipeline with Spark session."""
        self.app_name = app_name
        self.spark = None
        self.sc = None
        self.data = None
        self.cleaned_data = None
        self.parsed_data = None
        
    def initialize_spark(self):
        """Initialize Spark session and context."""
        try:
            logger.info("Initializing Spark session...")
            self.spark = (SparkSession.builder
                         .master('local')
                         .appName(self.app_name)
                         .getOrCreate())
            
            self.sc = self.spark.sparkContext
            logger.info("Spark session initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Spark: {str(e)}")
            raise
    
    def extract_data(self, file_path: str):
        """Extract data from CSV file."""
        try:
            logger.info(f"Extracting data from {file_path}...")
            
            # Read CSV with proper schema inference
            df = self.spark.read.csv(file_path, header=True, inferSchema=True)
            self.data = df.rdd
            
            logger.info(f"Data extracted successfully. Total records: {self.data.count()}")
            
        except Exception as e:
            logger.error(f"Failed to extract data: {str(e)}")
            raise
    
    def clean_data(self):
        """Clean and prepare data for analysis."""
        try:
            logger.info("Starting data cleaning process...")
            
            # Get column names
            columns = self.data.toDF().columns
            
            # Replace missing CustomerID values with "Unknown"
            self.cleaned_data = self.data.map(lambda row: Row(**{
                col: ("Unknown" if col == "CustomerID" and row[col] is None else row[col])
                for col in columns
            }))
            
            # Verify cleaning
            null_customers = self.cleaned_data.filter(lambda row: row['CustomerID'] is None).count()
            if null_customers == 0:
                logger.info("Data cleaning completed successfully")
            else:
                logger.warning(f"Still found {null_customers} null CustomerID values")
                
        except Exception as e:
            logger.error(f"Failed to clean data: {str(e)}")
            raise
    
    def parse_dates(self):
        """Parse date fields for time-based analysis."""
        try:
            logger.info("Parsing date fields...")
            
            self.parsed_data = self.cleaned_data.map(lambda row: Row(
                InvoiceNo=row['InvoiceNo'],
                StockCode=row['StockCode'],
                Description=row['Description'],
                Quantity=row['Quantity'],
                InvoiceDate=datetime.strptime(row['InvoiceDate'], "%m/%d/%Y %H:%M"),
                UnitPrice=row['UnitPrice'],
                CustomerID=row['CustomerID'],
                Country=row['Country']
            ))
            
            logger.info("Date parsing completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to parse dates: {str(e)}")
            raise
    
    def analyze_sales_overview(self):
        """Analyze overall sales metrics."""
        try:
            logger.info("Analyzing sales overview...")
            
            # Total transactions
            total_transactions = self.cleaned_data.map(lambda row: row['InvoiceNo']).distinct().count()
            
            # Total quantity sold
            total_quantity = self.cleaned_data.map(lambda row: row['Quantity']).sum()
            
            # Total revenue
            total_revenue = self.cleaned_data.map(lambda row: row['UnitPrice'] * row['Quantity']).sum()
            
            # Average order value
            avg_order_value = total_revenue / total_transactions if total_transactions > 0 else 0
            
            results = {
                'total_transactions': total_transactions,
                'total_quantity': total_quantity,
                'total_revenue': round(total_revenue, 2),
                'avg_order_value': round(avg_order_value, 2)
            }
            
            logger.info("Sales overview analysis completed")
            return results
            
        except Exception as e:
            logger.error(f"Failed to analyze sales overview: {str(e)}")
            raise
    
    def analyze_products(self):
        """Analyze product performance metrics."""
        try:
            logger.info("Analyzing product performance...")
            
            # Top products by quantity
            top_products_qty = (self.cleaned_data
                               .map(lambda row: (row['Description'], row['Quantity']))
                               .reduceByKey(lambda a, b: a + b)
                               .sortBy(lambda x: x[1], ascending=False)
                               .take(10))
            
            # Top products by revenue
            top_products_rev = (self.cleaned_data
                               .map(lambda row: (row['Description'], row['Quantity'] * row['UnitPrice']))
                               .reduceByKey(lambda a, b: round(a + b, 2))
                               .sortBy(lambda x: x[1], ascending=False)
                               .take(10))
            
            logger.info("Product analysis completed")
            return top_products_qty, top_products_rev
            
        except Exception as e:
            logger.error(f"Failed to analyze products: {str(e)}")
            raise
    
    def analyze_customers(self):
        """Analyze customer behavior metrics."""
        try:
            logger.info("Analyzing customer behavior...")
            
            # Filter out unknown customers
            known_customers = self.cleaned_data.filter(lambda row: row['CustomerID'] != "Unknown")
            
            # Top spending customers
            top_spending = (known_customers
                           .map(lambda row: (row['CustomerID'], row['Quantity'] * row['UnitPrice']))
                           .reduceByKey(lambda a, b: round(a + b, 2))
                           .sortBy(lambda x: x[1], ascending=False)
                           .take(10))
            
            # Top customers by purchase frequency
            top_frequency = (known_customers
                            .map(lambda row: (row['CustomerID'], 1))
                            .reduceByKey(lambda a, b: a + b)
                            .sortBy(lambda x: x[1], ascending=False)
                            .take(10))
            
            # Average order value per customer
            avg_order_per_customer = (known_customers
                                     .map(lambda row: (row['CustomerID'], (row['Quantity'] * row['UnitPrice'], 1)))
                                     .reduceByKey(lambda a, b: (a[0] + b[0], a[1] + b[1]))
                                     .mapValues(lambda x: round(x[0] / x[1], 2))
                                     .sortBy(lambda x: x[1], ascending=False)
                                     .take(10))
            
            logger.info("Customer analysis completed")
            return top_spending, top_frequency, avg_order_per_customer
            
        except Exception as e:
            logger.error(f"Failed to analyze customers: {str(e)}")
            raise
    
    def analyze_time_patterns(self):
        """Analyze time-based patterns in sales."""
        try:
            logger.info("Analyzing time patterns...")
            
            if not self.parsed_data:
                raise ValueError("Parsed data not available. Run parse_dates() first.")
            
            # Sales by month
            sales_by_month = (self.parsed_data
                             .map(lambda row: ((row.InvoiceDate.year, row.InvoiceDate.month), 
                                              row.Quantity * row.UnitPrice))
                             .reduceByKey(lambda a, b: round(a + b, 2))
                             .sortByKey()
                             .collect())
            
            # Sales by day
            sales_by_day = (self.parsed_data
                           .map(lambda row: (row.InvoiceDate.date(), row.Quantity * row.UnitPrice))
                           .sortByKey()
                           .collect())
            
            # Sales by hour
            sales_by_hour = (self.parsed_data
                            .map(lambda row: (row.InvoiceDate.hour, row.Quantity * row.UnitPrice))
                            .reduceByKey(lambda a, b: round(a + b, 2))
                            .sortByKey()
                            .collect())
            
            logger.info("Time pattern analysis completed")
            return sales_by_month, sales_by_day, sales_by_hour
            
        except Exception as e:
            logger.error(f"Failed to analyze time patterns: {str(e)}")
            raise
    
    def analyze_geographic_patterns(self):
        """Analyze geographic distribution of sales."""
        try:
            logger.info("Analyzing geographic patterns...")
            
            if not self.parsed_data:
                raise ValueError("Parsed data not available. Run parse_dates() first.")
            
            # Sales by country
            sales_by_country = (self.parsed_data
                               .map(lambda row: (row.Country, row.Quantity * row.UnitPrice))
                               .reduceByKey(lambda a, b: round(a + b, 2))
                               .sortBy(lambda x: x[1], ascending=False)
                               .collect())
            
            # Transactions by country
            transactions_by_country = (self.parsed_data
                                     .map(lambda row: (row.Country, row.InvoiceNo))
                                     .distinct()
                                     .map(lambda x: (x[0], 1))
                                     .reduceByKey(lambda a, b: a + b)
                                     .sortBy(lambda x: x[1], ascending=False)
                                     .collect())
            
            logger.info("Geographic analysis completed")
            return sales_by_country, transactions_by_country
            
        except Exception as e:
            logger.error(f"Failed to analyze geographic patterns: {str(e)}")
            raise
    
    def generate_report(self, results):
        """Generate and save analysis report."""
        try:
            logger.info("Generating analysis report...")
            
            report = f"""
ONLINE RETAIL ANALYSIS REPORT
============================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SALES OVERVIEW:
---------------
Total Transactions: {results['sales_overview']['total_transactions']:,}
Total Quantity Sold: {results['sales_overview']['total_quantity']:,}
Total Revenue: ${results['sales_overview']['total_revenue']:,.2f}
Average Order Value: ${results['sales_overview']['avg_order_value']:,.2f}

TOP PRODUCTS BY QUANTITY:
------------------------
"""
            
            for i, (product, qty) in enumerate(results['top_products_qty'], 1):
                report += f"{i}. {product}: {qty:,} units\n"
            
            report += f"""

TOP PRODUCTS BY REVENUE:
-----------------------
"""
            
            for i, (product, revenue) in enumerate(results['top_products_rev'], 1):
                report += f"{i}. {product}: ${revenue:,.2f}\n"
            
            report += f"""

TOP CUSTOMERS BY SPENDING:
-------------------------
"""
            
            for i, (customer_id, spending) in enumerate(results['top_spending_customers'], 1):
                report += f"{i}. Customer {customer_id}: ${spending:,.2f}\n"
            
            # Save report to file
            with open('retail_analysis_report.txt', 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info("Report generated and saved to 'retail_analysis_report.txt'")
            
        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}")
            raise
    
    def run_pipeline(self, file_path: str = 'dataset/retail_dataset.csv'):
        """Run the complete ETL pipeline."""
        try:
            logger.info("Starting ETL pipeline...")
            
            # Initialize Spark
            self.initialize_spark()
            
            # Extract
            self.extract_data(file_path)
            
            # Transform
            self.clean_data()
            self.parse_dates()
            
            # Analyze
            sales_overview = self.analyze_sales_overview()
            top_products_qty, top_products_rev = self.analyze_products()
            top_spending, top_frequency, avg_order_per_customer = self.analyze_customers()
            sales_by_month, sales_by_day, sales_by_hour = self.analyze_time_patterns()
            sales_by_country, transactions_by_country = self.analyze_geographic_patterns()
            
            # Compile results
            results = {
                'sales_overview': sales_overview,
                'top_products_qty': top_products_qty,
                'top_products_rev': top_products_rev,
                'top_spending_customers': top_spending,
                'top_customers_frequency': top_frequency,
                'avg_order_per_customer': avg_order_per_customer,
                'sales_by_month': sales_by_month,
                'sales_by_day': sales_by_day,
                'sales_by_hour': sales_by_hour,
                'sales_by_country': sales_by_country,
                'transactions_by_country': transactions_by_country
            }
            
            # Generate report
            self.generate_report(results)
            
            logger.info("ETL pipeline completed successfully!")
            return results
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise
        
        finally:
            # Cleanup
            if self.spark:
                self.spark.stop()
                logger.info("Spark session stopped")


def main():
    """Main function to run the ETL pipeline."""
    try:
        # Create and run pipeline
        pipeline = RetailETLPipeline()
        results = pipeline.run_pipeline()
        
        # Print summary
        print("\n" + "="*50)
        print("ETL PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*50)
        print(f"Total Revenue: ${results['sales_overview']['total_revenue']:,.2f}")
        print(f"Total Transactions: {results['sales_overview']['total_transactions']:,}")
        print(f"Report saved to: retail_analysis_report.txt")
        print("="*50)
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 