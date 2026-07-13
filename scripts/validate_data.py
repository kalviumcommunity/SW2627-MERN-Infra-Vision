import os
import json
import pandas as pd
from datetime import datetime

try:
    import chardet
except ImportError:
    chardet = None

INPUT_FILE = "data/raw/cloud_data.csv"

EXPECTED_COLUMNS = [
    "BillingID",
    "ProjectID",
    "CloudService",
    "InfrastructureCost",
    "CPUUsage"
]


def validate_file_exists(filepath):
    if not os.path.exists(filepath):
        return False, "File not found"

    if os.path.getsize(filepath) == 0:
        return False, "File is empty"

    return True, "File exists"


def validate_file_format(filepath):
    extension = filepath.split(".")[-1].lower()

    if extension not in ["csv"]:
        return False, "Unsupported file format"

    return True, "CSV format verified"


def validate_schema(df):
    missing = set(EXPECTED_COLUMNS) - set(df.columns)

    if missing:
        return False, f"Missing columns: {missing}"

    return True, "Schema valid"


def detect_encoding(filepath):
    with open(filepath, "rb") as file:
        raw = file.read()

    if chardet is not None:
        result = chardet.detect(raw)
        if result and result.get("encoding"):
            return result["encoding"]

    return "utf-8"


def dataset_statistics(filepath, df):
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "file_size_mb": round(os.path.getsize(filepath)/(1024*1024),4)
    }


def generate_report():

    report = {
        "timestamp": datetime.now().isoformat(),
        "checks": {}
    }

    status, message = validate_file_exists(INPUT_FILE)
    report["checks"]["File Exists"] = message

    if not status:
        return report

    status, message = validate_file_format(INPUT_FILE)
    report["checks"]["File Format"] = message

    if not status:
        return report

    df = pd.read_csv(INPUT_FILE)

    status, message = validate_schema(df)
    report["checks"]["Schema"] = message

    report["checks"]["Encoding"] = detect_encoding(INPUT_FILE)

    report["Statistics"] = dataset_statistics(INPUT_FILE, df)

    os.makedirs("output", exist_ok=True)

    with open("output/intake_report.json","w") as file:
        json.dump(report,file,indent=4)

    return report


if __name__=="__main__":

    report = generate_report()

    print(report)