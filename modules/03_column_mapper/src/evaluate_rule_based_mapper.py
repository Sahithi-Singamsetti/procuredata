import pandas as pd
from pathlib import Path

from map_columns_rule_based import map_columns_rule_based


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "generated"
ANSWER_KEY_PATH = BASE_DIR / "data" / "answer_key.csv"
RESULTS_DIR = BASE_DIR / "results"


def evaluate_rule_based_mapper():

    answer_key = pd.read_csv(ANSWER_KEY_PATH)
    evaluation_records = []

    for file_path in sorted(DATA_DIR.glob("file_*.csv")):

        predictions = map_columns_rule_based(file_path)

        actual_file = answer_key[
            answer_key["file_name"] == file_path.name
        ]

        for _, prediction in predictions.iterrows():

            original_header = prediction["original_header"]

            actual_record = actual_file[
                actual_file["original_header"] == original_header
            ]

            actual_field = actual_record["standard_field"].iloc[0]
            predicted_field = prediction["standard_field"]

            evaluation_records.append({
                "file_name": file_path.name,
                "original_header": original_header,
                "actual_field": actual_field,
                "predicted_field": predicted_field,
                "score": prediction["score"],
                "status": prediction["status"],
                "correct": predicted_field == actual_field
            })

    return pd.DataFrame(evaluation_records)


def print_evaluation_summary(results):

    total_headers = len(results)

    matched_results = results[
        results["status"] == "matched"
    ]

    review_results = results[
        results["status"] == "needs_review"
    ]

    correct_matches = matched_results["correct"].sum()
    incorrect_matches = len(matched_results) - correct_matches

    accuracy = (
        correct_matches / len(matched_results) * 100
        if len(matched_results) > 0 else 0
    )

    coverage = (
        len(matched_results) / total_headers * 100
        if total_headers > 0 else 0
    )

    print("\nRULE-BASED MAPPER EVALUATION")
    print("-" * 40)

    print(f"Total headers: {total_headers}")
    print(f"Automatically mapped: {len(matched_results)}")
    print(f"Correct automatic mappings: {correct_matches}")
    print(f"Incorrect automatic mappings: {incorrect_matches}")
    print(f"Sent for human review: {len(review_results)}")

    print(f"\nAutomatic mapping accuracy: {accuracy:.2f}%")
    print(f"Mapping coverage: {coverage:.2f}%")


if __name__ == "__main__":

    results = evaluate_rule_based_mapper()

    print(results.to_string(index=False))

    print_evaluation_summary(results)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    output_path = RESULTS_DIR / "rule_based_evaluation_results.csv"

    results.to_csv(output_path, index=False)

    print(f"\nResults saved to: {output_path}")