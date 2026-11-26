import pandas as pd
from pathlib import Path

from map_columns import map_columns

# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data" / "generated"
ANSWER_KEY_PATH = BASE_DIR / "data" / "answer_key.csv"

def evaluate_mapper():

    # Step 1: Load the answer key
    answer_key = pd.read_csv(ANSWER_KEY_PATH)

    # Step 2: Store evaluation results
    all_results = []

    # Step 3: Process each generated CSV file
    for file_path in sorted(DATA_DIR.glob("file_*.csv")):

        file_name = file_path.name

        # Get the correct mappings for this file
        correct_mappings = answer_key[
            answer_key["file_name"] == file_name
        ]

        # Run our mapper
        predictions = map_columns(file_path)

        # Compare predictions with the answer key
        for _, prediction in predictions.iterrows():

            original_header = prediction["original_header"]

            actual_row = correct_mappings[
                correct_mappings["original_header"] == original_header
            ]

            if actual_row.empty:
                continue

            actual_field = actual_row.iloc[0]["standard_field"]

            all_results.append({
                "file_name": file_name,
                "original_header": original_header,
                "actual_field": actual_field,
                "predicted_field": prediction["standard_field"],
                "score": prediction["score"],
                "status": prediction["status"],
                "correct": prediction["standard_field"] == actual_field
            })

    return pd.DataFrame(all_results)

def print_evaluation_summary(results):

    total_headers = len(results)

    # Automatically accepted mappings
    matched_results = results[
        results["status"] == "matched"
    ]

    # Headers sent for human review
    review_results = results[
        results["status"] == "needs_review"
    ]

    correct_matches = matched_results["correct"].sum()

    incorrect_matches = len(matched_results) - correct_matches

    # Calculate automatic mapping accuracy
    if len(matched_results) > 0:
        accuracy = (correct_matches / len(matched_results)) * 100
    else:
        accuracy = 0

    # Calculate mapping coverage
    if total_headers > 0:
        coverage = (len(matched_results) / total_headers) * 100
    else:
        coverage = 0

    print("\n========== MAPPER EVALUATION ==========")

    print(f"Total headers: {total_headers}")
    print(f"Automatically mapped: {len(matched_results)}")
    print(f"Correct automatic mappings: {correct_matches}")
    print(f"Incorrect automatic mappings: {incorrect_matches}")
    print(f"Sent for human review: {len(review_results)}")

    print(f"\nAutomatic mapping accuracy: {accuracy:.2f}%")
    print(f"Mapping coverage: {coverage:.2f}%")

    print("=======================================\n")

if __name__ == "__main__":

    # Run evaluation
    results = evaluate_mapper()

    # Display detailed results
    print("\n========== DETAILED RESULTS ==========")
    print(results.to_string(index=False))

    # Display summary metrics
    print_evaluation_summary(results)

    # Save results to CSV
    output_path = BASE_DIR / "results" / "evaluation_results.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    results.to_csv(output_path, index=False)

    print(f"Results saved to: {output_path}")