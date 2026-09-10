# FlowCart — End-to-End E-Commerce Data Engineering Pipeline

FlowCart is an end-to-end data engineering project that simulates how e-commerce order data can move from raw source files through validation, incremental processing, cloud orchestration, distributed transformation, and analytics-ready modeling.

The project was built to practice the complete lifecycle of a modern data pipeline rather than focusing on a single tool.

## Project Objective

The source data intentionally contains realistic data-quality problems such as:

- duplicate records
- missing values
- invalid quantities
- malformed dates
- invalid customer and product references
- invalid product prices
- new and updated orders arriving in a later batch

The objective was to build a pipeline that could detect these issues, separate invalid records, process new data incrementally, and prepare reliable datasets for downstream analytics.

---

## Architecture

```text
Raw CSV Files
      ↓
Python / Pandas ETL
      ↓
Data Validation & Quarantine
      ↓
PostgreSQL
      ↓
Azure Blob Storage
      ↓
Azure Data Factory
      ↓
Bronze Layer
      ↓
Azure Databricks / PySpark
      ↓
Delta Lake
      ↓
dbt Transformations & Tests
      ↓
Analytics-Ready Models
```

### Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Source | CSV | Simulated operational e-commerce data |
| ETL | Python / Pandas | Cleaning, validation and incremental processing |
| Database | PostgreSQL | Relational storage and SQL analysis |
| Cloud Storage | Azure Blob Storage | Raw and bronze data storage |
| Orchestration | Azure Data Factory | Batch ingestion and pipeline orchestration |
| Distributed Processing | Databricks / PySpark | Scalable transformations |
| Lakehouse | Delta Lake | Incremental MERGE, versioning and time travel |
| Transformation | dbt | SQL modeling and automated data-quality tests |

---

## Dataset

The project contains three main business entities:

### Customers

Customer information including customer ID, name, city, segment and signup date.

### Products

Product information including product ID, product name, category and unit price.

### Orders

Transactional data containing:

- order ID
- customer ID
- product ID
- quantity
- order date
- order status
- last modified timestamp

Two order batches were used to simulate historical and incremental ingestion.

---

## 1. Python / Pandas ETL

The first stage of the project uses Python and Pandas to inspect and validate raw source data.

The pipeline checks for:

- duplicate records
- missing customer references
- invalid product references
- invalid quantities
- malformed dates
- invalid product prices

Invalid records are separated from valid data rather than silently passing through the pipeline.

This creates a simple quarantine approach that preserves problematic records for investigation.

### Initial Order Batch

The initial order dataset contained:

**3,001 raw order records**

After validation and data-quality handling, the dataset was prepared for downstream processing.

---

## 2. Incremental Processing

A second order batch was introduced to simulate new data arriving after the initial load.

The batch contained:

- **251 new orders**
- **50 updated existing orders**

Instead of rebuilding the complete dataset from scratch, the ETL logic distinguishes between new and existing order IDs.

Existing records are updated while new records are appended.

After incremental processing:

- final unique order IDs: **3,246**
- duplicate order IDs: **0**

This demonstrates the difference between a full historical load and incremental data processing.

---

## 3. PostgreSQL

Validated data was loaded into a relational PostgreSQL database.

The database contains:

```text
customers
products
orders
```

Primary and foreign-key relationships were used to maintain referential integrity.

Final database load:

- **500 customers**
- **98 products**
- **3,188 valid orders**

Records containing invalid foreign-key references were excluded from the production tables rather than violating database constraints.

### SQL Analysis

SQL exercises included:

- multi-table joins
- aggregations
- revenue analysis
- CTEs
- window functions
- `ROW_NUMBER`
- `RANK`
- `DENSE_RANK`
- top-N analysis
- query execution plans
- indexing concepts
- `EXPLAIN ANALYZE`

The project therefore covers both pipeline engineering and downstream SQL analysis.

---

## 4. Azure Blob Storage

The project was then extended from local processing into Azure.

Azure Blob Storage was used to create separate storage layers.

```text
raw/
bronze/
```

Raw source files are stored without modification in the raw layer.

This preserves the original input and separates source data from downstream processing.

---

## 5. Azure Data Factory

Azure Data Factory was used as the orchestration layer.

A linked service connects ADF to Azure Blob Storage.

Datasets were created for the raw and bronze order files, and a Copy Data activity was used to move incoming data through the ingestion pipeline.

Example:

```text
raw/orders_batch_1.csv
        ↓
Azure Data Factory
        ↓
bronze/orders_batch_1.csv
```

A second batch demonstrates how later data arrivals can be processed independently instead of repeatedly copying the entire historical dataset.

ADF is therefore responsible for **orchestration and ingestion**, while transformation logic is handled by the processing layers.

---

## 6. Databricks / PySpark

The bronze data was processed in Azure Databricks using PySpark.

Spark DataFrames were used to work with the ingested data and demonstrate distributed transformation concepts.

This stage introduced concepts including:

- Spark DataFrames
- distributed processing
- partitioning
- transformation of bronze data
- scalable processing compared with local Pandas workflows

Pandas was used earlier for local ETL and validation, while Spark represents the distributed processing layer of the architecture.

---

## 7. Delta Lake

Processed data was stored using Delta Lake.

Delta provides capabilities beyond standard CSV or Parquet storage, including:

- ACID transactions
- table versioning
- schema-aware storage
- incremental updates
- historical versions

### Incremental MERGE

Instead of replacing the entire target table when new data arrives, Delta `MERGE` was used to handle updates and inserts.

Conceptually:

```text
WHEN MATCHED
    → UPDATE existing order

WHEN NOT MATCHED
    → INSERT new order
```

This mirrors a common production pattern for incremental pipelines.

### Time Travel

Delta table history was inspected to view previous versions of the dataset.

Time travel makes it possible to query earlier table states, which can be useful for:

- debugging
- auditing
- investigating pipeline changes
- recovering historical data

---

## 8. dbt Analytics Engineering

dbt was added as the final transformation and data-quality layer.

dbt connects to the PostgreSQL database and builds SQL models on top of the underlying data.

The project includes staging and business-oriented transformations.

Example business model:

```sql
select
    status,
    count(*) as total_orders,
    sum(quantity) as total_units
from {{ ref('stg_orders') }}
group by status
order by total_orders desc
```

### Automated Tests

dbt tests were added to validate the order identifier.

The pipeline checks that `order_id` is:

```text
NOT NULL
UNIQUE
```

The final test execution completed successfully:

```text
PASS=2
WARN=0
ERROR=0
```

This provides an additional automated data-quality layer on top of the earlier Python validation and PostgreSQL constraints.

---

## Data Quality Strategy

Data quality is checked at multiple stages rather than relying on a single validation step.

```text
Raw Data
   ↓
Pandas validation
   ↓
Quarantine invalid records
   ↓
PostgreSQL constraints
   ↓
Spark / Delta processing
   ↓
dbt automated tests
```

This layered approach helps prevent invalid data from silently reaching analytical models.

---

## Key Results

The completed project demonstrates:

- processing of **3,001 initial raw orders**
- detection and quarantine of data-quality issues
- incremental processing of **251 new + 50 updated orders**
- **3,246 unique order IDs** after incremental processing
- relational modeling in PostgreSQL
- Azure cloud storage using raw and bronze layers
- ADF-based batch orchestration
- distributed processing with PySpark
- Delta Lake incremental `MERGE`
- Delta version history and time travel
- dbt transformation models
- automated `unique` and `not_null` tests

---

## Engineering Decisions

Several architectural decisions were intentionally made during the project.

### Full Load vs Incremental Load

The initial dataset represents the historical load.

The second batch represents incremental ingestion.

Only newly arrived or modified records need to be processed instead of rebuilding the entire historical dataset.

### Pandas vs Spark

Pandas is appropriate for the small local dataset used during initial development and validation.

PySpark was introduced to demonstrate how the same pipeline architecture can scale when datasets become too large for single-machine processing.

### Quarantine vs Deletion

Invalid records are separated for investigation instead of simply being deleted.

This preserves traceability and makes data-quality failures observable.

### Raw vs Bronze Storage

Raw storage preserves the original source files.

The bronze layer represents data that has entered the managed pipeline and can be processed by downstream systems.

---

## What This Project Demonstrates

FlowCart combines several areas of data engineering in one project:

**ETL:** Python, Pandas, validation and data cleaning

**Data Engineering:** incremental loads, referential integrity and pipeline design

**SQL:** PostgreSQL, joins, CTEs, window functions and query optimization

**Cloud:** Azure Blob Storage and Azure Data Factory

**Big Data:** Databricks and PySpark

**Lakehouse:** Delta Lake, MERGE and time travel

**Analytics Engineering:** dbt models and automated tests

The main focus is not the individual technologies themselves, but how they interact across an end-to-end data pipeline.

---

## Future Improvements

Possible production-oriented extensions include:

- parameterized ADF pipelines
- automated pipeline retries and failure notifications
- API-based ingestion as an additional source
- scheduled dbt jobs
- additional dbt relationship and accepted-value tests
- CI/CD
- secrets management with Azure Key Vault
- monitoring and logging
- larger datasets for Spark performance testing

These were kept outside the current implementation to keep the project focused on the core end-to-end pipeline.

---

## Project Status

**Completed end-to-end portfolio implementation.**

The project covers the path from intentionally imperfect raw source data through validation, incremental processing, cloud ingestion, distributed transformation, Delta Lake storage, and tested analytics models.