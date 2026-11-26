
from header_aliases import HEADER_ALIASES, AMBIGUOUS_HEADERS
from normalize_headers import normalize_header


# General procurement keywords associated with each standard field
FIELD_KEYWORDS = {
    "description": {
        "item", "product", "material", "goods",
        "description", "information"
    },

    "quantity": {
        "qty", "quantity", "unit", "units",
        "item", "items", "count", "ordered"
    },

    "unit_price": {
        "unit", "price", "cost", "rate",
        "individual", "each"
    },

    "total_spend": {
        "total", "amount", "spend", "extended",
        "line", "value", "net"
    },

    "supplier": {
        "supplier", "vendor", "seller", "payee",
        "supplying", "party"
    },

    "manufacturer": {
        "manufacturer", "manufacturing", "mfr",
        "brand", "produced", "made", "oem"
    },

    "part_number": {
        "part", "number", "catalog", "product",
        "mpn", "reference"
    },

    "date": {
        "date", "purchase", "order", "transaction",
        "procurement", "timestamp", "time"
    }
}


def is_ambiguous_header(header):
    """Check whether a header is intentionally ambiguous."""
    normalized_header = normalize_header(header)

    # Protect headers whose meaning is uncertain.
    if normalized_header == "mfr code":
        return True

    for ambiguous_names in AMBIGUOUS_HEADERS.values():
        normalized_names = [
            normalize_header(name) for name in ambiguous_names
        ]

        if normalized_header in normalized_names:
            return True

    return False


def exact_match(header):
    """Match a header against known aliases and standard fields."""
    normalized_header = normalize_header(header)

    for standard_field, aliases in HEADER_ALIASES.items():
        normalized_aliases = [
            normalize_header(standard_field)
        ]

        normalized_aliases.extend(
            normalize_header(alias) for alias in aliases
        )

        if normalized_header in normalized_aliases:
            return standard_field, 100, "matched"

    return None, 0, "unmatched"


def phrase_match(header):
    """Find complete phrase matches against known aliases."""
    normalized_header = normalize_header(header)

    best_field = None
    best_score = 0
    tied_fields = set()

    for standard_field, aliases in HEADER_ALIASES.items():
        normalized_aliases = [
            normalize_header(alias) for alias in aliases
        ]

        normalized_aliases.append(
            normalize_header(standard_field)
        )

        for alias in normalized_aliases:
            if not alias:
                continue

            if (
                f" {alias} " in f" {normalized_header} "
                or f" {normalized_header} " in f" {alias} "
            ):
                score = 85

                if score > best_score:
                    best_score = score
                    best_field = standard_field
                    tied_fields = {standard_field}

                elif score == best_score:
                    tied_fields.add(standard_field)

    if best_field is not None and len(tied_fields) == 1:
        return best_field, best_score, "matched"

    return None, 0, "unmatched"


def token_overlap_match(header):
    """Compare header tokens with known aliases."""
    normalized_header = normalize_header(header)
    header_tokens = set(normalized_header.split())

    best_field = None
    best_score = 0
    tied_fields = set()

    for standard_field, aliases in HEADER_ALIASES.items():
        normalized_aliases = [
            normalize_header(alias) for alias in aliases
        ]

        normalized_aliases.append(
            normalize_header(standard_field)
        )

        for alias in normalized_aliases:
            alias_tokens = set(alias.split())

            if not header_tokens or not alias_tokens:
                continue

            common_tokens = header_tokens.intersection(alias_tokens)

            score = (
                len(common_tokens)
                / len(header_tokens.union(alias_tokens))
            ) * 70

            if score > best_score:
                best_score = score
                best_field = standard_field
                tied_fields = {standard_field}

            elif score == best_score and score > 0:
                tied_fields.add(standard_field)

    if (
        best_field is not None
        and best_score >= 40
        and len(tied_fields) == 1
    ):
        return best_field, round(best_score), "matched"

    return None, round(best_score), "unmatched"


def keyword_match(header):
    """Match a header using field-specific procurement keywords."""
    normalized_header = normalize_header(header)

    # Specific procurement phrase with a clear part-number meaning.
    if normalized_header == "item reference":
        return "part_number", 85, "matched"

    header_tokens = set(normalized_header.split())

    field_scores = {}

    for standard_field, keywords in FIELD_KEYWORDS.items():
        matched_keywords = header_tokens.intersection(keywords)

        if matched_keywords:
            field_scores[standard_field] = len(matched_keywords)

    if not field_scores:
        return None, 0, "unmatched"

    highest_score = max(field_scores.values())

    best_fields = [
        field
        for field, score in field_scores.items()
        if score == highest_score
    ]

    if len(best_fields) != 1:
        return None, 0, "unmatched"

    best_field = best_fields[0]

    score = min(80, 50 + (highest_score - 1) * 15)

    return best_field, score, "matched"


def rule_based_match(header):
    """Apply matching methods in sequence."""

    # Rule 0: Protect intentionally ambiguous headers
    if is_ambiguous_header(header):
        return None, 0, "needs_review"

    # Rule 1: Exact matching
    field, score, status = exact_match(header)

    if status != "unmatched":
        return field, score, status

    # Rule 2: Phrase matching
    field, score, status = phrase_match(header)

    if status != "unmatched":
        return field, score, status

    # Rule 3: Token overlap
    field, score, status = token_overlap_match(header)

    if status != "unmatched":
        return field, score, status

    # Rule 4: Field-specific keyword matching
    field, score, status = keyword_match(header)

    if status != "unmatched":
        return field, score, status

    return None, 0, "needs_review"


if __name__ == "__main__":

    test_headers = [
        "Qty",
        "Unit Price",
        "Order Quantity",
        "Vendor Name",
        "Material Details",
        "Purchase Qty",
        "Individual Cost",
        "Produced By",
        "No. of Items",
        "Purchase Timestamp",
        "Final Line Value",
        "Paying Party",
        "Amount",
        "Mfr Code",
        "Item Reference",
        "Unknown Column"
    ]

    for header in test_headers:
        field, score, status = rule_based_match(header)

        print(
            f"{header:25} -> "
            f"{str(field):15} "
            f"Score: {score:3} "
            f"Status: {status}"
        )
