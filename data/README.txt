Mini Azure E-Commerce ETL Project - Starter Data

Files
-----
customers.csv
products.csv
orders_batch_1.csv
orders_batch_2.csv

The data intentionally contains quality problems:
- duplicates
- NULL/blank values
- invalid negative or zero quantities
- invalid date text
- orphan product IDs
- an invalid negative product price
- updated orders in batch 2

Do NOT clean the source files manually. The point of the project is to detect,
decide how to handle, and transform these issues in the ETL pipeline.
