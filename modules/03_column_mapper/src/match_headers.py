from rapidfuzz import fuzz, process

from header_aliases import HEADER_ALIASES, AMBIGUOUS_HEADERS
from normalize_headers import normalize_header


def match_header(header):
    """
    Find the best matching standard field for a column header.
    """

    normalized_header = normalize_header(header)

    best_field = None
    best_score = 0

    # Step 1: Check for ambiguous headers
    for standard_field, ambiguous_names in AMBIGUOUS_HEADERS.items():

        normalized_ambiguous = [
            normalize_header(name) for name in ambiguous_names
        ]

        if normalized_header in normalized_ambiguous:
            return None, 0, "needs_review"

    # Step 2: Check for exact matches
    for standard_field, aliases in HEADER_ALIASES.items():

        normalized_aliases = [
            normalize_header(standard_field)
        ]

        normalized_aliases.extend(
            normalize_header(alias) for alias in aliases
        )

        if normalized_header in normalized_aliases:
            return standard_field, 100, "matched"

    # Step 3: Find the closest fuzzy match
    for standard_field, aliases in HEADER_ALIASES.items():

        normalized_aliases = [
            normalize_header(standard_field)
        ]

        normalized_aliases.extend(
            normalize_header(alias) for alias in aliases
        )

        result = process.extractOne(
            normalized_header,
            normalized_aliases,
            scorer=fuzz.ratio
        )

        if result is not None:
            _, score, _ = result

            if score > best_score:
                best_score = score
                best_field = standard_field

    # Step 4: Apply the minimum matching threshold
    
    if best_score >= 70:
        return best_field, round(best_score), "matched"

    return None, round(best_score), "needs_review"


def get_confidence_level(score):
    """
    Classify a matching score into a confidence category.
    """

    if score >= 90:
        return "High"

    elif score >= 70:
        return "Medium"

    else:
        return "Low"