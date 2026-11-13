
from pathlib import Path
import importlib

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


# Import the validation module
validate_data = importlib.import_module(
    "modules.02_data_quality.src.validate_data"
)


# Project paths
MODULE_DIR = Path(__file__).resolve().parents[1]
REPORT_DIR = MODULE_DIR / "reports"
REPORT_FILE = REPORT_DIR / "data_quality_report.xlsx"


# Expected columns for the issue details sheet
ISSUE_COLUMNS = [
    "file_name",
    "row_number",
    "column",
    "issue_type",
    "actual_value",
]


def collect_report_data():
    """Collect quality scores and validation issues for all datasets."""

    files = [validate_data.CLEAN_FILE] + sorted(
        validate_data.INPUT_DIR.glob("purchases_*.csv")
    )

    summary_records = []
    all_issues = []

    # Reuse the same loaded DataFrame for all validation checks.
    validation_checks = [
        validate_data.check_blank_values,
        validate_data.check_invalid_prices,
        validate_data.check_non_numeric_values,
        validate_data.check_incorrect_totals,
        validate_data.check_duplicate_rows,
        validate_data.check_invalid_dates,
    ]

    for file_path in files:
        data = validate_data.load_purchase_file(file_path)
        file_issues = []

        for check in validation_checks:
            file_issues.extend(
                check(data, file_path.name)
            )

        score = validate_data.calculate_quality_score(
            len(data),
            len(file_issues),
        )

        summary_records.append({
            "file_name": file_path.name,
            "total_records": len(data),
            "issues_found": len(file_issues),
            "quality_score": score,
        })

        all_issues.extend(file_issues)

    summary_df = pd.DataFrame(
        summary_records,
        columns=[
            "file_name",
            "total_records",
            "issues_found",
            "quality_score",
        ],
    )

    # Preserve the expected columns even when no issues are found.
    issues_df = pd.DataFrame(
        all_issues,
        columns=ISSUE_COLUMNS,
    )

    return summary_df, issues_df


def format_excel_report():
    """Apply formatting to the generated Excel workbook."""

    workbook = load_workbook(REPORT_FILE)

    header_fill = PatternFill(
        start_color="1F4E78",
        end_color="1F4E78",
        fill_type="solid",
    )

    header_font = Font(
        bold=True,
        color="FFFFFF",
    )

    for worksheet in workbook.worksheets:

        # Format header row
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center")

        # Keep headers visible while scrolling
        worksheet.freeze_panes = "A2"

        # Enable column filters
        worksheet.auto_filter.ref = worksheet.dimensions

        # Adjust column widths based on content
        for column_cells in worksheet.columns:
            max_length = max(
                len(str(cell.value or ""))
                for cell in column_cells
            )

            column_letter = get_column_letter(
                column_cells[0].column
            )

            worksheet.column_dimensions[column_letter].width = min(
                max_length + 3,
                45,
            )

    workbook.save(REPORT_FILE)

def generate_excel_report():
    """Generate the Excel data-quality report."""

    summary_df, issues_df = collect_report_data()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(REPORT_FILE, engine="openpyxl") as writer:
        summary_df.to_excel(
            writer,
            sheet_name="Summary",
            index=False,
        )

        issues_df.to_excel(
            writer,
            sheet_name="Issue Details",
            index=False,
        )

    format_excel_report()

    print("Excel report generated successfully!")
    print(f"Report location: {REPORT_FILE}")
    print(f"Datasets analyzed: {len(summary_df)}")
    print(f"Total issues detected: {len(issues_df)}")


if __name__ == "__main__":
    generate_excel_report()
