from pathlib import Path
import pandas as pd

# Locate the NASA dataset

PROJECT_ROOT = Path(__file__).resolve().parents[3]

data_folder = PROJECT_ROOT / "data" / "raw" / "spend_analytics"

csv_files = list(data_folder.glob("*.csv"))

if not csv_files:
    print("No CSV file found!")
else:
    file_path = csv_files[0]

    print("Dataset:", file_path.name)

    df = pd.read_csv(file_path, nrows=5, low_memory=False)

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nFirst 5 records:")
    print(df.to_string(index=False))

    print("\nNumber of columns:", len(df.columns))