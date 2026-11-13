import sys
import importlib
from pathlib import Path
import pandas as pd
import pytest


# Add the project root to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))


# Import the validation module
validate_data = importlib.import_module(
    "modules.02_data_quality.src.validate_data"
)


# Project paths
MODULE_DIR = Path(__file__).resolve().parents[1]
INPUT_DIR = MODULE_DIR / "data" / "input"
CLEAN_FILE = MODULE_DIR / "data" / "generated" / "purchases_clean.csv"


def test_clean_dataset_has_no_issues():
    """Verify that the clean dataset produces zero issues."""

    issues = validate_data.validate_purchase_file(CLEAN_FILE)

    assert len(issues) == 0


@pytest.mark.parametrize(
    "file_name, expected_issues",
    [
        ("purchases_01.csv", 3),
        ("purchases_02.csv", 5),
        ("purchases_03.csv", 3),
        ("purchases_04.csv", 2),
        ("purchases_05.csv", 6),
    ],
)
def test_corrupted_datasets_detect_expected_issues(file_name, expected_issues):
    """Verify that every corrupted dataset produces the expected issue count."""

    file_path = INPUT_DIR / file_name

    issues = validate_data.validate_purchase_file(file_path)

    assert len(issues) == expected_issues


@pytest.mark.parametrize(
    "total_records, issue_count, expected_score",
    [
        (1000, 0, 100.0),
        (1000, 19, 98.1),
        (1000, 1000, 0.0),
        (0, 0, 0.0),
    ],
)
def test_quality_score(total_records, issue_count, expected_score):
    """Verify quality score calculations."""

    score = validate_data.calculate_quality_score(
        total_records,
        issue_count,
    )

    assert score == expected_score

def test_detected_issues_match_answer_key():
    """Verify detected issues against the independently created answer key."""

    answer_key_path = MODULE_DIR / "data" / "answer_key.csv"
    answer_key = pd.read_csv(answer_key_path)

    expected_issues = set(
        zip(
            answer_key["file_name"],
            answer_key["row_number"],
            answer_key["column"],
            answer_key["issue_type"],
        )
    )

    detected_issues = set()

    files = sorted(INPUT_DIR.glob("purchases_*.csv"))

    for file_path in files:
        issues = validate_data.validate_purchase_file(file_path)

        for issue in issues:
            detected_issues.add(
                (
                    issue["file_name"],
                    issue["row_number"],
                    issue["column"],
                    issue["issue_type"],
                )
            )

    assert detected_issues == expected_issues