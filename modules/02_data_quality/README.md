
# Data Quality Checker

## Project Overview

The Data Quality Checker is a Python-based tool developed to identify common data-quality issues in procurement purchase records.

The project uses synthetically generated purchase datasets containing 1,000 records. Five copies of the clean dataset are modified with deliberately planted errors to test the validation system.

The tool analyzes each dataset, identifies data-quality issues, calculates a quality score, and generates an Excel report containing a summary and detailed issue records.

## Project Objectives

- Generate synthetic purchase records.
- Introduce controlled data-quality issues.
- Detect errors automatically using Python.
- Calculate a data-quality score for each dataset.
- Generate an Excel report with issue details and row numbers.
- Verify detection accuracy using an independent answer key and automated tests.

## Dataset Details

### Data Source

- Source: Synthetically generated using Python and the Faker library.
- Original dataset: `purchases_clean.csv`
- Number of records: 1,000
- Corrupted datasets: Five copies of the original dataset.
- Total deliberately planted issues: 19.
- External data source: Not applicable. No real procurement or personal data is used.

### Field Definitions

| Field | Description |
|---|---|
| date | Date of purchase |
| supplier | Name of the supplier |
| item | Purchased item |
| quantity | Number of units purchased |
| unit_price | Price per unit |
| total | Total purchase amount (quantity x unit price) |

### Dataset Files

| File | Description |
|---|---|
| `purchases_clean.csv` | Original clean dataset |
| `purchases_01.csv` | Contains blank values |
| `purchases_02.csv` | Contains invalid prices and non-numeric values |
| `purchases_03.csv` | Contains incorrect totals and duplicate records |
| `purchases_04.csv` | Contains future and incorrectly formatted dates |
| `purchases_05.csv` | Contains multiple types of data-quality issues |

The independent `answer_key.csv` file records the expected location and category of each deliberately introduced issue.

## Data Quality Checks

The validation system performs the following checks:

| Check | Description |
|---|---|
| Blank Values | Identifies missing or empty field values. |
| Invalid Prices | Detects zero or negative unit prices. |
| Non-Numeric Values | Identifies text or invalid numeric values in quantity, unit_price, and total fields. |
| Incorrect Totals | Checks whether quantity x unit_price matches the recorded total. A tolerance of 0.01 is allowed. |
| Duplicate Records | Identifies completely duplicated purchase records. |
| Invalid Dates | Detects incorrectly formatted dates and dates later than the current date. |

The input file structure is also checked to ensure that all six expected columns are present in the correct order.

### Quality Scoring

Each dataset receives a quality score between 0 and 100.

The scoring formula is:

```text
Quality Score = max(0, 100 - (Issues Found / Total Records x 100))
```

The score is rounded to two decimal places.

- A dataset with no detected issues receives a score of 100.
- An empty dataset receives a score of 0.
- The score cannot fall below 0.

The score represents the proportion of detected issues relative to the number of records. It is a simple project-specific metric rather than a universal data-quality standard.

## How to Run

Run the following commands from the ProcureIQ project root directory.

### Prerequisites

- Python 3.11 or later
- Pandas
- Faker
- OpenPyXL
- Pytest (for automated testing)

Install the required packages if they are not already available:

```powershell
pip install pandas Faker openpyxl pytest
```

### 1. Generate the clean dataset

```powershell
python -m modules.02_data_quality.src.generate_data
```

This generates 1,000 synthetic purchase records and saves them to:

`modules/02_data_quality/data/generated/purchases_clean.csv`

### 2. Introduce data-quality issues

```powershell
python -m modules.02_data_quality.src.introduce_errors
```

This creates five corrupted datasets in the input directory and generates the independent answer key.

### 3. Run data validation and generate the Excel report

```powershell
python -m modules.02_data_quality.src.generate_report
```

The generated Excel report is saved to:

`modules/02_data_quality/reports/data_quality_report.xlsx`

The workbook contains two sheets:

- **Summary:** Dataset names, record counts, detected issue counts, and quality scores.
- **Issue Details:** Individual issues, including file names, row numbers, affected columns, issue types, and actual values.

### 4. Run automated tests

```powershell
pytest modules/02_data_quality/tests/test_validate_data.py -v
```

The test suite verifies clean and corrupted datasets, quality-score calculations, and detection results against the independent answer key.

## Project Structure

```text
02_data_quality/
|
|-- data/
|   |-- generated/
|   |   |-- purchases_clean.csv
|   |
|   |-- input/
|   |   |-- purchases_01.csv
|   |   |-- purchases_02.csv
|   |   |-- purchases_03.csv
|   |   |-- purchases_04.csv
|   |   |-- purchases_05.csv
|   |
|   |-- answer_key.csv
|
|-- notebooks/
|
|-- reports/
|   |-- data_quality_report.xlsx
|
|-- src/
|   |-- generate_data.py
|   |-- introduce_errors.py
|   |-- validate_data.py
|   |-- generate_report.py
|
|-- tests/
|   |-- test_validate_data.py
|
|-- README.md
```

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Dataset loading and processing |
| Faker | Synthetic purchase-data generation |
| CSV | Dataset storage and file handling |
| Decimal | Accurate financial calculations |
| OpenPyXL | Excel report generation and formatting |
| Pytest | Automated testing |

## Testing Results

The current automated test suite contains 11 tests.

All 11 tests pass, including verification that the 19 detected issues match the independently generated answer key.
