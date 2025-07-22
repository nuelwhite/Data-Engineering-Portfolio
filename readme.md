# E-Commerce Transactions Data Cleaning Challenge

## Scenario
You're a data engineer intern at a growing e-commerce startup. The analytics team provided a massive CSV file with 8 million transaction records from the past year. The data is messy, inconsistent, and too large to load into memory on most machines. Your mission: clean and standardize the data efficiently and in a memory-friendly way.

## Dataset Description
The dataset (`transactions.csv`) contains the following columns:

| Column             | Description                                         |
|--------------------|-----------------------------------------------------|
| `customer_id`      | ID of the customer (some are missing)              |
| `transaction_id`   | Unique transaction string like `TXN1234567`        |
| `purchase_amount`  | Sometimes a float, sometimes a string, sometimes blank |
| `currency`         | Should be all 'USD', but has lowercase/missing     |
| `purchase_date`    | Mixed formats like `'2023/01/01'`, `'01-02-2023'`  |
| `product_id`       | Product ID, might be null                          |
| `product_category` | Category like 'Electronics', 'Books', messy casing |
| `is_returned`      | Values like `'yes'`, `True`, `'no'`, `False`, NaN  |

## Memory Usage Insights
- Loading the full 8M-row dataset at once can use over 2GB of RAM, which is not feasible for many systems.
- Loading a 100,000-row sample uses much less memory and is suitable for exploration and prototyping.
- Chunked reading and processing is essential for handling large files efficiently.

## Data Cleaning & Transformation Steps
The following steps were applied to clean and standardize the data:

1. **Drop Duplicates:**
   - Remove duplicate rows to ensure data integrity.
2. **Handle Missing Values:**
   - Drop rows with missing `purchase_amount`.
3. **Convert Data Types:**
   - `customer_id`: Convert to nullable integer, then to category for memory efficiency.
   - `transaction_id`: Convert to string.
   - `product_id`: Convert to category.
   - `currency`: Standardize to 'USD' and convert to category.
   - `purchase_date`: Clean and parse mixed date formats to datetime.
   - `product_category`: Standardize casing and convert to category.
   - `is_returned`: Map all variants to boolean.
4. **Standardize Values:**
   - Normalize currency and product category values for consistency.
5. **Optimize Column Order:**
   - Reorder columns for logical grouping and easier analysis.

## Memory Optimization Results
- After cleaning and type conversions, memory usage dropped from over 30MB to about 7MB for a 100k-row sample.
- The same approach scales to millions of rows when using chunked processing.

## Chunked Processing for Large Files
To process the full dataset efficiently, the script reads and processes the CSV in chunks (default: 100,000 rows at a time), applies all cleaning and transformation steps, and writes the cleaned data to a new file incrementally.

## How to Run
1. Place your raw CSV at `data/raw/transactions.csv`.
2. Run the script:
   ```bash
   python challenge.py
   ```
3. The cleaned output will be saved to `data/processed/transactions_cleaned.csv`.

## Logging
- Processing progress and memory usage are logged to `logs/processing.log` and the console.

## Key Takeaways
- Always explore and prototype on a small sample before scaling to the full dataset.
- Use chunked processing for large files to avoid memory issues.
- Data type conversions and value standardization are crucial for both memory efficiency and data quality.

