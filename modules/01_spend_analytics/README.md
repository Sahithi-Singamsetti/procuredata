
# Module 1: Spend Analytics

## Overview

Spend Analytics is the first implemented module of ProcureData, a procurement analytics platform designed to support procurement data processing, spending analysis, supplier insights, and data-driven decision-making.

This module analyses NASA federal procurement contract transactions from FY2025 to identify spending patterns, supplier distribution, monthly trends, and procurement categories.

## Dataset

| Parameter | Details |
|---|---|
| Source | USAspending.gov |
| Agency | NASA |
| Award Type | Contracts |
| Fiscal Year | FY2025 |
| Action Date Range | October 1, 2024 to September 30, 2025 |
| Download Date | November 2, 2026 |
| Original Records | 21,051 |
| Original Columns | 297 |
| Selected Columns | 10 |

The original dataset is preserved separately from the selected and cleaned datasets.

The ten selected fields cover transaction identifiers, award identifiers, action dates, federal obligations, recipient information, product or service codes, and NAICS classifications.

## Technology Stack

- Python 3.11
- Pandas
- NumPy
- PostgreSQL 18.6
- Psycopg
- SQL
- Streamlit
- Plotly
- Pytest
- Python-dotenv

## Key Features

- Total net procurement obligation analysis
- Monthly spending trends
- Top supplier analysis
- Procurement category breakdown
- KPI cards for net spend, unique suppliers, awards, and transactions
- Interactive date, supplier, and category filters
- Transaction-level details
- Filtered CSV export (up to 500 records)
- SQL-based analytical queries
- PostgreSQL-backed dashboard

## Project Structure

```text
modules/
└── 01_spend_analytics/
    ├── README.md
    ├── prepare_data.py
    ├── clean_data.py
    ├── load_data.py
    ├── schema.sql
    ├── analysis.sql
    ├── notebooks/
    │   ├── inspect_dataset.py
    │   └── analyze_dataset.py
    ├── src/
    │   ├── __init__.py
    │   └── cleaning.py
    └── tests/
        └── test_clean_data.py
```

## Data Processing Workflow

The module follows this processing sequence:

1. **Dataset preparation:** Selects the required ten columns from the original USAspending dataset and creates an intermediate CSV.
2. **Data cleaning:** Standardizes and validates transaction data and generates the cleaned dataset.
3. **Database setup:** Creates the PostgreSQL table using the provided schema.
4. **Data loading:** Loads cleaned transactions into PostgreSQL using the transaction unique key to prevent duplicate inserts.
5. **Data analysis:** Executes SQL queries for spending, monthly trends, suppliers, categories, and supplier concentration.
6. **Dashboard visualization:** Presents interactive KPIs, charts, filters, and transaction details using Streamlit and Plotly.

## Database

- Database: `procureiq`
- Main table: `spend_transactions`
- Database system: PostgreSQL 18.6
- Primary key: `contract_transaction_unique_key`

Database connection settings are managed through environment variables in a local `.env` file.

The `.env` file is excluded from version control. Use `.env.example` as the configuration template.

## Project Scripts

| File | Description |
|---|---|
| `prepare_data.py` | Selects the required columns and creates the intermediate dataset |
| `clean_data.py` | Cleans and validates transaction data |
| `load_data.py` | Loads cleaned records into PostgreSQL |
| `schema.sql` | Defines the PostgreSQL table |
| `analysis.sql` | Contains analytical SQL queries |

### Exploratory Scripts

The following scripts are maintained in the `notebooks/` directory:

| File | Description |
|---|---|
| `inspect_dataset.py` | Inspects the original dataset structure and sample records |
| `analyze_dataset.py` | Performs exploratory data analysis and examines spending patterns |

## Setup and Execution

Run the following commands from the ProcureData project root directory.

### 1. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a local `.env` file:

```powershell
Copy-Item .env.example .env
```

Update the database credentials in `.env` to match your local PostgreSQL configuration.

### 4. Create the PostgreSQL database

Create a database named `procureiq` in PostgreSQL.

For example, using `psql`:

```powershell
psql -U <YOUR_POSTGRES_USER> -d postgres -c "CREATE DATABASE procureiq;"
```

Replace `<YOUR_POSTGRES_USER>` with your local PostgreSQL username.

Create the Module 1 table:

```powershell
psql -U <YOUR_POSTGRES_USER> -d procureiq -f modules/01_spend_analytics/schema.sql
```

### 5. Download and prepare the dataset

Download the NASA FY2025 contract transaction dataset from USAspending.gov.

Place the downloaded CSV in:

```text
data/raw/spend_analytics/
```

Run the preparation and cleaning scripts:

```powershell
python modules/01_spend_analytics/prepare_data.py
python modules/01_spend_analytics/clean_data.py
```

Load the cleaned data into PostgreSQL:

```powershell
python modules/01_spend_analytics/load_data.py
```

### 6. Launch the dashboard

```powershell
streamlit run app.py
```

## Running Tests

Run the Module 1 unit tests from the project root:

```powershell
python -m pytest modules/01_spend_analytics/tests/ -v
```

## Validation Summary

The FY2025 NASA dataset contains:

| Validation Metric | Result |
|---|---:|
| Total transactions | 21,051 |
| Unique transaction identifiers | 21,051 |
| Duplicate transaction identifiers | 0 |
| Exact duplicate rows | 0 |
| Missing obligation amounts | 0 |
| Invalid dates | 0 |
| Negative obligation records | 1,701 |
| Zero obligation records | 6,460 |
| Missing NAICS classifications | 1 |
| Unique supplier UEIs | 2,910 |
| Unique award identifiers | 9,365 |

Negative obligations represent adjustments and are retained in the analysis. Zero-obligation transactions are also retained.

One transaction has a missing NAICS classification, which is preserved as missing rather than assigned an assumed category.

Detailed financial reconciliation, business definitions, and validation findings are documented in:

`docs/data_dictionary/module1_validation.md`

## Current Limitations

- Supplier names are not always unique identifiers; 40 supplier names are associated with multiple UEIs.
- Supplier identity definitions require consistent treatment across supplier rankings and concentration analysis.
- The dashboard transaction export is limited to the latest 500 matching records.
- The Pareto analysis is available in the SQL analysis, but its dashboard presentation is still pending.
- The category breakdown represents the selected top ten categories rather than the complete category distribution.
- Additional cleaning edge-case tests and integration tests are planned.

## Status

Core data preparation, cleaning, PostgreSQL loading, analytical SQL queries, and dashboard functionality are implemented.

Initial unit testing and dashboard validation have been completed. Final audit refinements, additional test coverage, and documentation improvements are underway.
