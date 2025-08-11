# Retail Transactions Analytics with Pyspark RDDs

---

This project simulates a real-world ***retail transactions data pipeline*** that processes large, messy datasets using only RDDs (No DataFrames). 

The project demonstrates an end-to-end *ETL* and *analytics*, highlighting key RDD transformations, actions, and more.

---

## Project Workflow

1. Load the data 
    
    using textFile()

2. Clean the data

3. Perform Transformations

    map() for parsing and transformations
    filter()
    distinct()
    reduceByKey()
    groupByKey()... etc.

4. Actions
    
    collect()
    take()
    count()
    saveAsTextFile() to save the transformed work

---

<u>**Analytics to showcase**</u>

* Total sales per category (reduceByKey)
* Top 10 best-selling products (sortBy + take)
* Revenue by location (join customers → reduceByKey)
* Customer purchase history (groupByKey)
* Average order value per customer (mapValues + reduceByKey + division)
* Peak sales hours (extract hour from timestamp → reduceByKey)


---

