import numpy as np
import pandas as pd

try:
    from .common import PROCESSED_DATA_FILE, ensure_output_dir, load_csv
except ImportError:
    from common import PROCESSED_DATA_FILE, ensure_output_dir, load_csv

def min_max_scale(values):
    minimum = values.min()
    maximum = values.max()
    span = maximum - minimum

    if span == 0:
        return np.zeros_like(values, dtype=float)

    return (values - minimum) / span


def z_score_scale(values):
    mean = values.mean()
    std_dev = values.std()

    if std_dev == 0:
        return np.zeros_like(values, dtype=float)

    return (values - mean) / std_dev


def add_vectorized_features(df):
    numeric_columns = ["InfrastructureCost", "CPUUsage"]

    for column in numeric_columns:
        if column not in df.columns:
            continue

        values = df[column].to_numpy(dtype=float)

        df[f"{column}_normalized"] = min_max_scale(values)
        df[f"{column}_zscore"] = z_score_scale(values)

    return df


def main():
    if not PROCESSED_DATA_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {PROCESSED_DATA_FILE}")

    df = load_csv(PROCESSED_DATA_FILE)
    df = add_vectorized_features(df)

    ensure_output_dir()
    df.to_csv(PROCESSED_DATA_FILE, index=False)

    print("Vectorized features added successfully!")
    print(df.head())


if __name__ == "__main__":
    main()