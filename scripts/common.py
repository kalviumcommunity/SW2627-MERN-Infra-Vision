from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
OUTPUT_DIR = BASE_DIR / "output"

RAW_DATA_FILE = RAW_DATA_DIR / "cloud_data.csv"
PROCESSED_DATA_FILE = OUTPUT_DIR / "processed_cloud_data.csv"
INTAKE_REPORT_FILE = OUTPUT_DIR / "intake_report.json"
PROFILE_REPORT_FILE = OUTPUT_DIR / "data_profile_report.txt"
DATA_DICTIONARY_FILE = OUTPUT_DIR / "data_dictionary.csv"
DISTRIBUTION_DIR = OUTPUT_DIR / "distribution"
DISTRIBUTION_REPORT_FILE = DISTRIBUTION_DIR / "distribution_analysis.json"


def ensure_output_dir():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def ensure_distribution_dir():
    DISTRIBUTION_DIR.mkdir(parents=True, exist_ok=True)


def load_csv(path):
    return pd.read_csv(path)
