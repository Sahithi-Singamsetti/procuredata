
# ProcureIQ

ProcureIQ is a procurement analytics platform designed to support procurement data processing, spend analysis, supplier insights, and data-driven decision-making using analytics, machine learning, and automation.

The project is planned to include seven modules. Spend Analytics (Module 1) is the first implemented module; the remaining modules are currently scaffolded for future development.

## Project Architecture

- `app.py`: Main Streamlit application entry point
- `pages/`: Streamlit pages for individual modules
- `modules/`: Module-specific implementations
- `shared/`: Reusable utilities and database connections
- `data/`: Raw, intermediate, processed, and reference data organization
- `docs/`: Architecture, data dictionaries, and validation reports
- `tests/`: Unit and integration test organization

## Module Status

| Module | Description | Status |
|---|---|---|
| 1 | Spend Analytics | Implemented; audit refinements underway |
| 2 | Data Quality Checker | Scaffolded |
| 3 | Smart Column Mapper | Scaffolded |
| 4 | Supplier Name Matching | Scaffolded |
| 5 | Product Classification | Scaffolded |
| 6 | Price Benchmarking | Scaffolded |
| 7 | Part Number Extraction | Scaffolded |

## Technology Stack

- Python 3.11
- Pandas and NumPy
- PostgreSQL
- SQL
- Streamlit
- Plotly
- Scikit-learn
- Psycopg
- Pytest

## Prerequisites

- Python 3.11
- PostgreSQL
- Git
- Access to public award data from USAspending.gov

## Windows Setup (PowerShell)

### 1. Clone the repository

```powershell
git clone <REPOSITORY_URL>
cd ProcureIQ
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file using the provided template:

```powershell
Copy-Item .env.example .env
```

Update the database credentials in `.env` with your local PostgreSQL settings.

Never commit `.env` or database credentials.

### 5. Create the PostgreSQL database

Create a PostgreSQL database named `procureiq`.

```powershell
psql -U <YOUR_POSTGRES_USER> -d postgres -c "CREATE DATABASE procureiq;"
```

Run the Module 1 schema:

```powershell
psql -U <YOUR_POSTGRES_USER> -d procureiq -f modules/01_spend_analytics/schema.sql
```

### 6. Prepare the dataset

Download the NASA FY2025 contract transaction dataset from USAspending.gov.

- Agency: NASA
- Award type: Contracts
- Fiscal year: 2025
- Action date range: October 1, 2024 to September 30, 2025
- Dataset download date: November 2, 2026

Place the downloaded CSV in:

`data/raw/spend_analytics/`

The preparation script saves `spend_selected.csv` to `data/interim/spend_analytics/`. The cleaning script saves `spend_cleaned.csv` to `data/processed/spend_analytics/`. The database loader then imports the cleaned dataset into PostgreSQL.

Then run:

```powershell
python modules/01_spend_analytics/prepare_data.py
python modules/01_spend_analytics/clean_data.py
python modules/01_spend_analytics/load_data.py
```

### 7. Run the application

```powershell
streamlit run app.py
```

## Running Tests

Run the Module 1 unit tests:

```powershell
python -m pytest modules/01_spend_analytics/tests/ -v
```

## Module 1: Spend Analytics

The first module provides:

- Procurement spend analysis
- Monthly spend trends
- Top supplier analysis
- Product and service category breakdown
- Interactive date, supplier, and category filters
- Transaction-level details
- Filtered CSV export

The dashboard uses PostgreSQL queries and displays results based on the selected filters.

## Data and Documentation

- Detailed dataset validation: `docs/data_dictionary/module1_validation.md`
- Module 1 documentation: `modules/01_spend_analytics/README.md`
- Architecture documentation: `docs/architecture/README.md`

Raw and generated datasets, local database credentials, and virtual environments are excluded from version control.

## Current Limitations

- Only Spend Analytics is implemented.
- Modules 2–7 are currently scaffolds.
- The dashboard transaction export is limited to the latest 500 matching records.
- Additional shared utilities and integration tests are planned.
