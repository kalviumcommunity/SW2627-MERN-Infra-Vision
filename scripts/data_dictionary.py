import os
import pandas as pd

try:
    from .common import DATA_DICTIONARY_FILE, PROCESSED_DATA_FILE, ensure_output_dir, load_csv
except ImportError:
    from common import DATA_DICTIONARY_FILE, PROCESSED_DATA_FILE, ensure_output_dir, load_csv

def build_dictionary(df):
    dictionary = []

    for column in df.columns:
        data_type = str(df[column].dtype)

        if data_type == "object":
            business_type = "Categorical"
        elif "int" in data_type or "float" in data_type:
            business_type = "Numerical"
        else:
            business_type = "Other"

        dictionary.append(
            {
                "Column Name": column,
                "Data Type": data_type,
                "Business Type": business_type,
                "Missing Values": df[column].isnull().sum(),
                "Unique Values": df[column].nunique(),
                "Description": "",
            }
        )

    return pd.DataFrame(dictionary)


def main():
    if not PROCESSED_DATA_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {PROCESSED_DATA_FILE}")

    df = load_csv(PROCESSED_DATA_FILE)

    print("=" * 60)
    print("DATA DICTIONARY")
    print("=" * 60)

    dictionary_df = build_dictionary(df)
    print(dictionary_df)

    ensure_output_dir()
    dictionary_df.to_csv(DATA_DICTIONARY_FILE, index=False)

    print("\nData Dictionary saved successfully!")


if __name__ == "__main__":
    main()