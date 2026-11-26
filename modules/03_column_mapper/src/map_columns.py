
import pandas as pd

from match_headers import match_header, get_confidence_level


def map_columns(file_path):
    """
    Map CSV columns to standard procurement fields
    using one-to-one assignment.
    """

    # Step 1: Read the CSV file
    df = pd.read_csv(file_path)

    # Step 2: Get the original column headers
    original_headers = df.columns.tolist()

    # Step 3: Generate matching suggestions
    candidates = []

    for header in original_headers:

        standard_field, score, status = match_header(header)

        candidates.append({
            "original_header": header,
            "standard_field": standard_field,
            "score": score,
            "status": status
        })

    # Step 4: Sort candidates by score, highest first
    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    # Step 5: Enforce one-to-one assignment
    assigned_fields = set()
    mapping_results = []

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

        # Step 6: Determine confidence
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

    # Step 7: Restore original CSV column order
    results = pd.DataFrame(mapping_results)

    results["original_order"] = results["original_header"].map(
        {header: index for index, header in enumerate(original_headers)}
    )

    results = results.sort_values("original_order")
    results = results.drop(columns=["original_order"])

    return results.reset_index(drop=True)
