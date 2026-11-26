import re

def normalize_header(header):
    """
    Standardize a column header for easier comparison.
    """

    header = header.lower()

    header = re.sub(r"[^a-z0-9\s]", " ", header)

    header = re.sub(r"\s+", " ", header)

    return header.strip()
