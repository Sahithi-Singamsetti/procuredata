
# ProcureData

ProcureData is a procurement analytics platform designed to support procurement data processing, spend analysis, data quality assessment, supplier insights, and data-driven decision-making using analytics, machine learning, and automation.

The project is organized into seven modules, each addressing a different stage of the procurement analytics workflow. The first two modules have been implemented, with the remaining modules planned for progressive development and integration.

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
| 1 | Spend Analytics | Implemented |
| 2 | Data Quality Checker | Implemented |
| 3 | Smart Column Mapper | Scaffolded |
| 4 | Supplier Name Matching | Scaffolded |
| 5 | Product Classification | Scaffolded |
| 6 | Price Benchmarking | Scaffolded |
| 7 | Part Number Extraction | Scaffolded |

## Implemented Modules

### Module 1: Spend Analytics

Analyzes procurement transaction data to identify spending patterns and generate actionable insights.

Key features:

- Procurement spend analysis
- Monthly spend trends
- Top supplier analysis
- Product and service category breakdown
- Interactive date, supplier, and category filters
- Transaction-level details
- Filtered CSV export

The module uses PostgreSQL queries to retrieve and analyze procurement transaction data. Its Streamlit interface displays results based on the selected filters.

Documentation: `modules/01_spend_analytics/README.md`

### Module 2: Data Quality Checker

A Python-based validation tool that identifies common data-quality issues in procurement purchase records.

Key features:

- Synthetic purchase-data generation using Faker
- Controlled error injection across five test datasets
- Blank-value detection
- Zero and negative price detection
- Non-numeric value detection
- Incorrect total validation with a one-cent tolerance
- Duplicate record detection
- Invalid and future date detection
- Data-quality scoring on a scale of 0–100
- Automated Excel report generation

The module uses an independent answer key to verify that all deliberately introduced issues are detected correctly.

Testing results:

- 1,000 clean purchase records
- Five corrupted datasets
- 19 deliberately planted issues
- All 19 issues detected correctly
- Zero false alarms on the clean dataset
- 11 automated tests passing

Documentation: `modules/02_data_quality/README.md`

## Technology Stack

- Python 3.11
- Pandas and NumPy
- PostgreSQL
- SQL
- Streamlit
- Plotly
- Scikit-learn
- Psycopg
- Faker
- OpenPyXL
- Pytest

## Prerequisites

- Python 3.11
- PostgreSQL (required for Module 1)
- Git
- Access to public award data from USAspending.gov (required for Module 1)

## Windows Setup (PowerShell)

### 1. Clone the repository

```powershell
git clone <REPOSITORY_URL>
cd procuredata
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

Create a PostgreSQL database named `procureiq`:

```powershell
psql -U <YOUR_POSTGRES_USER> -d postgres -c "CREATE DATABASE procureiq;"
```

Run the Module 1 schema:

```powershell
psql -U <YOUR_POSTGRES_USER> -d procureiq -f modules/01_spend_analytics/schema.sql
```

### 6. Prepare the Module 1 dataset

Download the NASA FY2025 contract transaction dataset from USAspending.gov.

Dataset parameters:

- Agency: NASA
- Award type: Contracts
- Fiscal year: 2025
- Action date range: October 1, 2024 to September 30, 2025
- Dataset download date: November 2, 2026

Place the downloaded CSV in:

`data/raw/spend_analytics/`

The preparation script saves `spend_selected.csv` to `data/interim/spend_analytics/`. The cleaning script saves `spend_cleaned.csv` to `data/processed/spend_analytics/`. The database loader imports the cleaned dataset into PostgreSQL.

Run the following commands from the project root:

```powershell
python modules/01_spend_analytics/prepare_data.py
python modules/01_spend_analytics/clean_data.py
python modules/01_spend_analytics/load_data.py
```

## Running the Modules

### Module 1: Spend Analytics

Requires PostgreSQL and the prepared NASA procurement dataset.

```powershell
streamlit run app.py
```

### Module 2: Data Quality Checker

Generate the clean synthetic purchase dataset:

```powershell
python -m modules.02_data_quality.src.generate_data
```

Introduce controlled data-quality issues and generate the independent answer key:

```powershell
python -m modules.02_data_quality.src.introduce_errors
```

Generate the Excel data-quality report:

```powershell
python -m modules.02_data_quality.src.generate_report
```

The generated datasets, answer key, and Excel report are stored within:

`modules/02_data_quality/data/`

`modules/02_data_quality/reports/`

## Running Tests

Run the Module 1 tests:

```powershell
python -m pytest modules/01_spend_analytics/tests/ -v
```

Run the Module 2 tests:

```powershell
python -m pytest modules/02_data_quality/tests/ -v
```

Run the complete project test suite:

```powershell
python -m pytest -v
```

Current test results:

- Module 1: 14 tests passing
- Module 2: 11 tests passing
- Total: 25 tests passing

## Data and Documentation

- Module 1 documentation: `modules/01_spend_analytics/README.md`
- Module 2 documentation: `modules/02_data_quality/README.md`
- Module 1 dataset validation: `docs/data_dictionary/module1_validation.md`
- Architecture documentation: `docs/architecture/README.md`

Raw and generated datasets, local database credentials, and virtual environments are excluded from version control where appropriate.

## Development Roadmap

The remaining modules will progressively extend the platform:

- Module 3: Smart Column Mapper
- Module 4: Supplier Name Matching
- Module 5: Product Classification
- Module 6: Price Benchmarking
- Module 7: Part Number Extraction

Once the individual modules are implemented, the project will move into an integration and presentation phase, with a unified dashboard, consistent navigation, and improved user experience.

## Current Limitations

- Modules 3–7 are still under development.
- The unified dashboard integrating all seven modules is planned for the final development phase.
- The Module 1 dashboard transaction export is currently limited to the latest 500 matching records.
- Additional shared utilities and integration tests are planned.
