import pandas as pd

from rule_based_matcher import rule_based_match
from match_headers import get_confidence_level


def map_columns_rule_based(file_path):
    """
    Map CSV columns to standard procurement fields
    using rule-based matching and one-to-one assignment.
    """

    df = pd.read_csv(file_path)
    original_headers = df.columns.tolist()

    candidates = []

    # Generate a matching result for each header
    for header in original_headers:

        standard_field, score, status = rule_based_match(header)

        candidates.append({
            "original_header": header,
            "standard_field": standard_field,
            "score": score,
            "status": status
        })

    # Process higher-scoring matches first
    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    assigned_fields = set()
    mapping_results = []

    # Enforce one-to-one field assignment
    for candidate in candidates:

        standard_field = candidate["standard_field"]
        score = candidate["score"]
        status = candidate["status"]

        if status == "needs_review":
            final_field = None
            final_status = "needs_review"

        elif standard_field in assigned_fields:
            final_field = None
            final_status = "needs_review"

        else:
            final_field = standard_field
            final_status = "matched"
            assigned_fields.add(standard_field)

        if final_status == "needs_review":
            confidence = "Review"
        else:
            confidence = get_confidence_level(score)

        mapping_results.append({
            "original_header": candidate["original_header"],
            "standard_field": final_field,
            "score": score,
            "status": final_status,
            "confidence": confidence
        })

    results = pd.DataFrame(mapping_results)

    # Restore the original CSV column order
    results["original_order"] = results["original_header"].map(
        {
            header: index
            for index, header in enumerate(original_headers)
        }
    )

    results = results.sort_values("original_order")
    results = results.drop(columns=["original_order"])

    return results.reset_index(drop=True)