import pandas as pd

INPUT_FILE = "data/raw/cloud_data.csv"
OUTPUT_FILE = "output/processed_cloud_data.csv"


def ingest_data(filepath):
    """
    Read cloud operational data from a CSV file.
    """
    df = pd.read_csv(filepath)
    print(f"Loaded {len(df)} records")
    return df


def process_data(df):
    """
    Clean the dataset.
    """
    df = df.drop_duplicates()
    df = df.fillna(0)
    print("Data cleaned successfully")
    return df


def output_results(df, filepath):
    """
    Save processed data to a CSV file.
    """
    df.to_csv(filepath, index=False)
    print(f"Processed data saved to {filepath}")


if __name__ == "__main__":
    data = ingest_data(INPUT_FILE)
    processed_data = process_data(data)
    output_results(processed_data, OUTPUT_FILE)