import pandas as pd


import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

customers = pd.read_csv("data/customers.csv")
products = pd.read_csv("data/products.csv")
orders = pd.read_csv("data/orders_batch_1.csv")


orders_batch_2 = pd.read_csv("data/orders_batch_2.csv")

from sqlalchemy import create_engine

from sqlalchemy import create_engine, text


print("CUSTOMERS")
print(customers.head())

print("\nPRODUCTS")
print(products.head())

print("\nORDERS")
print(orders.head())

print("\nORDER SHAPE")
print(orders.shape)

print("\nNULL VALUES")
print(orders.isna().sum())

print("\nDUPLICATES")
print(orders.duplicated().sum())



print("\nMISSING CUSTOMER IDs")
print(orders[orders["customer_id"].isna()])

print("\nINVALID QUANTITIES")
print(orders[orders["quantity"] <= 0])

print("\nINVALID ORDER DATES")
orders["parsed_order_date"] = pd.to_datetime(
    orders["order_date"],
    errors="coerce"
)

print(orders[orders["parsed_order_date"].isna()])

print("\nDUPLICATE ORDERS")
print(orders[orders.duplicated(keep=False)])

# Remove exact duplicates
orders_clean = orders.drop_duplicates().copy()

# Identify invalid records
invalid_mask = (
    orders_clean["customer_id"].isna()
    | (orders_clean["quantity"] <= 0)
    | orders_clean["parsed_order_date"].isna()
)

# Separate valid and invalid records
orders_quarantine = orders_clean[invalid_mask].copy()
orders_clean = orders_clean[~invalid_mask].copy()

print("\nCLEAN ORDERS:", len(orders_clean))
print("QUARANTINED ORDERS:", len(orders_quarantine))


print("\nINVALID PRODUCT REFERENCES")

invalid_products = orders_clean[
    ~orders_clean["product_id"].isin(products["product_id"])
]

print(invalid_products)

orders_clean["product_id"].isin(products["product_id"])

# Move invalid product references to quarantine
orders_quarantine = pd.concat(
    [orders_quarantine, invalid_products],
    ignore_index=True
)

# Keep only orders with valid product references
orders_clean = orders_clean[
    orders_clean["product_id"].isin(products["product_id"])
].copy()

print("\nFINAL CLEAN ORDERS:", len(orders_clean))
print("FINAL QUARANTINED ORDERS:", len(orders_quarantine))

invalid_customers = orders_clean[
    ~orders_clean["customer_id"].isin(customers["customer_id"])
]

print("\nINVALID CUSTOMER REFERENCES")
print(invalid_customers)


print("\nPRODUCT NULLS")
print(products.isna().sum())

print("\nPRODUCT DUPLICATES")
print(products.duplicated().sum())

print("\nINVALID PRODUCT PRICES")
print(products[products["unit_price"] <= 0])


# Create clean product dataset
products_clean = products.drop_duplicates().copy()

# Identify products with invalid prices
invalid_product_mask = (
    products_clean["unit_price"].isna()
    | (products_clean["unit_price"] <= 0)
)

# Separate valid and invalid products
products_quarantine = products_clean[invalid_product_mask].copy()
products_clean = products_clean[~invalid_product_mask].copy()

print("\nCLEAN PRODUCTS:", len(products_clean))
print("QUARANTINED PRODUCTS:", len(products_quarantine))

print("\nQUARANTINED PRODUCT RECORDS")
print(products_quarantine)


# Load processed data
orders_clean.to_csv(
    "data/processed/orders_clean.csv",
    index=False
)

products_clean.to_csv(
    "data/processed/products_clean.csv",
    index=False
)

# Load quarantined data
orders_quarantine.to_csv(
    "data/quarantine/orders_quarantine.csv",
    index=False
)

products_quarantine.to_csv(
    "data/quarantine/products_quarantine.csv",
    index=False
)

print("\nETL COMPLETE")



print("\nBATCH 2 SHAPE")
print(orders_batch_2.shape)

print("\nBATCH 2 SAMPLE")
print(orders_batch_2.head())

print("\nBATCH 2 NULLS")
print(orders_batch_2.isna().sum())

print("\nBATCH 2 DUPLICATES")
print(orders_batch_2.duplicated().sum())

new_orders = orders_batch_2[
    ~orders_batch_2["order_id"].isin(orders_clean["order_id"])
]

print("\nNEW ORDERS:", len(new_orders))

existing_orders = orders_batch_2[
    orders_batch_2["order_id"].isin(orders_clean["order_id"])
]

print("EXISTING ORDERS:", len(existing_orders))
print(existing_orders)


comparison = existing_orders.merge(
    orders_clean[["order_id", "last_modified"]],
    on="order_id",
    suffixes=("_new", "_old")
)

print("\nCOMPARISON")
print(comparison[
    ["order_id", "last_modified_old", "last_modified_new"]
].head(10))


updated_orders = comparison[
    comparison["last_modified_new"] > comparison["last_modified_old"]
]

print("\nUPDATED ORDERS:", len(updated_orders))
print(updated_orders.head())


updated_order_ids = updated_orders["order_id"]

updated_records = orders_batch_2[
    orders_batch_2["order_id"].isin(updated_order_ids)
]

incremental_orders = pd.concat(
    [new_orders, updated_records],
    ignore_index=True
)

print("\nINCREMENTAL LOAD")
print("NEW:", len(new_orders))
print("UPDATED:", len(updated_records))
print("TOTAL TO PROCESS:", len(incremental_orders))

orders_without_updates = orders_clean[
    ~orders_clean["order_id"].isin(updated_order_ids)
].copy()


orders_final = pd.concat(
    [
        orders_without_updates,
        updated_records,
        new_orders
    ],
    ignore_index=True
)

orders_final = pd.concat(
    [
        orders_without_updates,
        updated_records,
        new_orders
    ],
    ignore_index=True
)


orders_final = orders_final.drop_duplicates(
    subset=["order_id"],
    keep="last"
)


print("\nFINAL INCREMENTAL RESULT")
print("OLD CLEAN ORDERS:", len(orders_clean))
print("UPDATED:", len(updated_records))
print("NEW:", len(new_orders))
print("FINAL TOTAL:", len(orders_final))

orders_final.to_csv(
    "data/processed/orders_after_batch_2.csv",
    index=False
)


print("\nFINAL DUPLICATE ORDER IDs:")
print(orders_final["order_id"].duplicated().sum())

print("FINAL UNIQUE ORDER IDs:")
print(orders_final["order_id"].nunique())



engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:"
    f"{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:"
    f"{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)
with engine.connect() as connection:
    result = connection.execute(text("SELECT current_database();"))
    print("\nCONNECTED TO:", result.scalar())

customers_db = customers[
    ["customer_id", "customer_name", "city", "segment", "signup_date"]
].copy()
customers_db = customers_db.drop_duplicates(subset=["customer_id"], keep="first")
print("\nCUSTOMER DUPLICATES:")
print(customers_db[customers_db["customer_id"].duplicated(keep=False)])


customers["segment"] = customers["segment"].fillna("Unknown")
#customers_db.to_sql(
 #   "customers",
  #  engine,
   # if_exists="append",
   # index=False
#)

#products_clean.to_sql(
   # "products",
   # engine,
   # if_exists="append",
   # index=False
#)

orders_db = orders_final[
    [
        "order_id",
        "customer_id",
        "product_id",
        "quantity",
        "order_date",
        "status",
        "last_modified"
    ]
].copy()
print("\nORDERS PRE-LOAD CHECK")
print("Rows:", len(orders_db))
print("Duplicate order IDs:", orders_db["order_id"].duplicated().sum())
print(
    "Invalid customers:",
    (~orders_db["customer_id"].isin(customers_db["customer_id"])).sum()
)
print(
    "Invalid products:",
    (~orders_db["product_id"].isin(products_clean["product_id"])).sum()
)
orders_db = orders_db[
    orders_db["customer_id"].isin(customers_db["customer_id"]) &
    orders_db["product_id"].isin(products_clean["product_id"])
].copy()

print("\nORDERS READY FOR DATABASE:", len(orders_db))
orders_db.to_sql(
    "orders",
    engine,
    if_exists="append",
    index=False
)

print("\nPOSTGRESQL LOAD COMPLETE")

