# Module 1: Spend Analytics

## 1. Project Overview

The Spend Analytics module is the first module of ProcureIQ, a procurement analytics platform designed to help organizations understand and analyze their procurement spending.

The module processes procurement transaction data, stores it in a PostgreSQL database, and presents interactive insights through a Streamlit dashboard.

Its primary objectives are:

- Analyze total procurement spending.
- Identify major suppliers and procurement categories.
- Track monthly spending patterns.
- Allow users to filter transactions by date, supplier, and category.
- Provide access to transaction-level details and CSV exports.

## 2. Dataset Overview

The Spend Analytics module uses federal procurement contract transaction data obtained from [USAspending.gov](https://www.usaspending.gov/).

### Dataset Selection Criteria

| Parameter | Selection |
|---|---|
| Award Type | Contracts |
| Awarding Agency | NASA |
| Recipient Location | United States |
| Date Type | Action Date |
| Start Date | October 1, 2024 |
| End Date | September 30, 2025 |
| Financial Year | FY2025 |

### Dataset Statistics

| Metric | Value |
|---|---:|
| Total Transactions | 21,051 |
| Original Columns | 297 |
| Selected Columns | 10 |
| Unique Suppliers (UEI) | 2,910 |
| Unique Awards | 9,365 |
| Dataset Format | CSV |

The original dataset was retained in the raw data directory. Ten relevant columns were selected for analysis and stored separately for processing.

## 3. Data Dictionary

The original dataset contains 297 columns. The following 10 columns were selected as relevant to procurement spend analysis.

| Column Name | PostgreSQL Data Type | Description | Unit / Format | Usage |
|---|---|---|---|---|
| contract_transaction_unique_key | TEXT (Primary Key) | Unique identifier for each contract transaction | Text identifier | Transaction identification |
| award_id_piid | TEXT (NOT NULL) | Procurement Instrument Identifier (PIID) of the award | Text identifier | Award counting |
| federal_action_obligation | NUMERIC(20, 2) (NOT NULL) | Amount obligated or de-obligated by a transaction | USD, 2 decimal places | Spending calculations |
| action_date | DATE (NOT NULL) | Date on which the transaction action occurred | YYYY-MM-DD | Date filtering and monthly analysis |
| recipient_uei | TEXT (NOT NULL) | Unique Entity Identifier of the supplier | Text identifier | Unique supplier counting |
| recipient_name | TEXT (NOT NULL) | Name of the supplier or recipient | Text | Supplier analysis |
| product_or_service_code | TEXT (Nullable) | Federal Product Service Code (PSC) | Text code | Procurement category analysis |
| product_or_service_code_description | TEXT (Nullable) | Description of the PSC | Text | Category identification |
| naics_code | TEXT (Nullable) | North American Industry Classification System code | Text code | Industry classification |
| naics_description | TEXT (Nullable) | Description of the NAICS code | Text | Industry identification ||

## 4. Data Preparation and Cleaning

The dataset was prepared using Python and the Pandas library.

### Processing Workflow

1. Loaded the original NASA procurement transaction CSV.
2. Selected 10 relevant columns from the original 297 columns.
3. Converted the action_date column into a date format.
4. Validated transaction identifiers, supplier information and financial values.
5. Checked for duplicate transaction identifiers and missing values.
6. Retained positive, negative and zero obligation amounts.
7. Saved the cleaned dataset for database loading.

### Data Storage

| Stage | File Location |
|---|---|
| Original dataset | data/raw/spend_analytics/ |
| Selected dataset | data/interim/spend_analytics/spend_selected.csv |
| Cleaned dataset | data/processed/spend_analytics/spend_cleaned.csv |

### Python Scripts

| Script | Purpose |
|---|---|
| modules/01_spend_analytics/prepare_data.py | Selects the 10 required columns |
| modules/01_spend_analytics/clean_data.py | Cleans and validates the selected dataset |
| modules/01_spend_analytics/load_data.py | Loads the cleaned records into PostgreSQL |

The original raw dataset was preserved without modification.

## 5. Database Integration

ProcureIQ uses PostgreSQL 18.6 as its relational database management system.

### Database Configuration

| Parameter | Value |
|---|---|
| Database | procureiq |
| Database System | PostgreSQL 18.6 |
| Main Table | spend_transactions |
| Records Loaded | 21,051 |
| Primary Key | contract_transaction_unique_key |

### Table Structure

The spend_transactions table stores the 10 selected procurement transaction fields.

- contract_transaction_unique_key is the primary key.
- federal_action_obligation is stored as NUMERIC(20,2).
- action_date is stored as DATE.
- Identifier and description fields are stored as TEXT.
- PSC and NAICS fields allow NULL values.

### Database Scripts

| File | Purpose |
|---|---|
| schema.sql | Creates the spend_transactions table |
| load_data.py | Loads cleaned transaction records into PostgreSQL |
| analysis.sql | Contains SQL queries for procurement spend analysis |

### Database Connection

A reusable database connection is implemented in:

shared/database/connection.py

Database credentials are maintained in a local .env file and are excluded from version control.

## 6. Business Definitions and Calculation Logic

The following definitions are used throughout the Spend Analytics module.

| Metric | Definition |
|---|---|
| Net Spend | Sum of federal_action_obligation across the selected transactions |
| Positive Obligations | Sum of positive federal_action_obligation values |
| Negative Obligations | Sum of negative federal_action_obligation values |
| Unique Suppliers | Count of distinct recipient_uei values |
| Total Awards | Count of distinct award_id_piid values |
| Total Transactions | Count of contract transaction records |
| Monthly Net Spend | Sum of transaction obligations grouped by action month |
| Procurement Categories | Grouping based on PSC codes |

### Important Business Rules

1. Positive obligation values represent additional obligations.
2. Negative obligation values represent de-obligations or adjustments.
3. Zero obligation values are retained because they are valid transaction records.
4. Net Spend includes positive and negative obligation values.
5. Supplier counts are based on Unique Entity Identifiers (UEIs), not supplier names.
6. Award counts use distinct award IDs (PIIDs).
7. FY2025 analysis is based on action dates from October 1, 2024, to September 30, 2025.
8. The cumulative award value is not summed across transaction records because it may be repeated across modifications.
9. PSC codes are used for procurement category analysis, while NAICS codes represent industry classifications.

## 7. Spend Analysis Results

The following results were obtained from the FY2025 NASA procurement transaction dataset.

### Overall Spending Metrics

| Metric | Result |
|---|---:|
| Net Obligations | $15,704,952,068.38 |
| Positive Obligations | $16,253,906,572.42 |
| Negative Obligations | -$548,954,504.04 |
| Unique Suppliers | 2,910 |
| Total Awards | 9,365 |
| Total Transactions | 21,051 |

### Monthly Net Obligations

| Month | Net Obligations (USD) |
|---|---:|
| October 2024 | $1,188,508,705.79 |
| November 2024 | $492,818,627.07 |
| December 2024 | $944,510,689.78 |
| January 2025 | $1,189,987,583.80 |
| February 2025 | $1,196,581,763.01 |
| March 2025 | $1,186,605,975.73 |
| April 2025 | $903,555,442.24 |
| May 2025 | $911,474,023.00 |
| June 2025 | $1,147,667,550.38 |
| July 2025 | $1,357,923,361.70 |
| August 2025 | $1,896,078,504.03 |
| September 2025 | $3,289,239,841.85 |

### Key Findings

- September 2025 recorded the highest monthly net obligations.
- November 2024 recorded the lowest monthly net obligations.
- The top 10 supplier-name groups accounted for approximately 56.88% of total net obligations. Supplier rankings are grouped by recipient name, while unique supplier counts are based on UEIs.
- California Institute of Technology was the largest supplier by net obligations.
- PSC code AR11 was the largest procurement category by net obligations.

## 8. Data Validation Results

The dataset was validated using Python and PostgreSQL queries.

### Validation Summary

| Validation Check | Result | Status |
|---|---:|---|
| Total transaction records | 21,051 | Passed |
| Duplicate transaction IDs | 0 | Passed |
| Missing transaction IDs | 0 | Passed |
| Missing supplier names | 0 | Passed |
| Missing supplier UEIs | 0 | Passed |
| Missing obligation amounts | 0 | Passed |
| Missing PSC codes | 0 | Passed |
| Missing NAICS codes | 1 | Review |
| Positive obligation transactions | 12,890 | Verified |
| Negative obligation transactions | 1,701 | Verified |
| Zero obligation transactions | 6,460 | Verified |

### Financial Reconciliation

The financial totals were independently checked:

Positive Obligations + Negative Obligations = Net Obligations

$16,253,906,572.42 + (-$548,954,504.04) = $15,704,952,068.38

The calculated net obligations match the database total.

### Missing NAICS Investigation

One transaction was found to have a missing NAICS code and description.

Investigation confirmed that both fields were already missing in the original NASA source CSV.

- Affected records: 1
- Total records: 21,051
- Missing percentage: 0.0048%
- Database representation: NULL
- Root cause: Missing information in the original source dataset.

The transaction was retained without modification. No NAICS code was inferred or assigned.

### Supplier Identity Validation

Forty supplier names were found to be associated with multiple UEIs.

These relationships were not automatically merged because different UEIs may represent distinct legal entities or registrations.

They will be investigated further in the Supplier Name Matching module.

## 9. Dashboard Features

The Spend Analytics dashboard is developed using Streamlit and Plotly.

### Key Performance Indicators (KPIs)

The dashboard displays four primary metrics:

- Total Net Spend
- Unique Suppliers
- Total Awards
- Total Transactions

### Visualizations

| Visualization | Purpose |
|---|---|
| Monthly Net Spending | Tracks spending trends across FY2025 |
| Top 10 Suppliers | Identifies suppliers with the highest net obligations |
| Top 10 Procurement Categories | Highlights major spending categories |
| Category Breakdown | Displays each of the top 10 categories as a percentage of their combined net spend |

### Interactive Filters

Users can filter the dashboard using:

- Start and end dates
- Supplier name
- PSC procurement category

All KPI metrics, charts and transaction details update according to the selected filters.

### Transaction Details and Export

The dashboard provides:

- A transaction-level data table.
- Up to 500 of the most recent matching transactions.
- CSV export functionality.
- Appropriate handling of empty results.

### Functional Testing

The dashboard was tested using:

1. Default FY2025 date range.
2. Date-only filtering.
3. Supplier-only filtering.
4. PSC category filtering.
5. Combined filters.
6. No-result scenarios.

All tested filtering and display functions worked as expected.

## 10. Limitations and Future Improvements

### Current Limitations

1. The analysis currently uses NASA FY2025 contract transaction data rather than procurement data from multiple agencies.
2. One transaction has a missing NAICS code and description in the original source dataset.
3. Forty supplier names are associated with multiple UEIs and require further entity-resolution investigation.
4. Transaction details are limited to the 500 most recent matching records in the dashboard.
5. The current dashboard uses PSC codes for procurement category analysis.

### Future Improvements

- Integrate procurement data from additional agencies and sources.
- Expand automated data quality checks and add end-to-end pipeline validation.
- Improve supplier name matching and entity resolution.
- Introduce product classification and price benchmarking.
- Develop advanced procurement analytics and reporting.
- Improve dashboard design and user experience.
- Explore role-based access and additional export formats.
