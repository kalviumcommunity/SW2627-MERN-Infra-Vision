from pathlib import Path
import subprocess
import sys

print("=" * 60)
print("INFRAVISION DATA PIPELINE")
print("=" * 60)

BASE_DIR = Path(__file__).resolve().parent.parent

 main
]

for label, title, command in initial_steps:
    print(f"\n{label} : {title}")
    subprocess.run(command, cwd=str(BASE_DIR), check=True)

extra_steps = [
    ("Step 6", "String Cleaning", [sys.executable, str(BASE_DIR / "scripts" / "string_cleaning.py")]),
    ("Step 7", "Date & Time Transformation", [sys.executable, str(BASE_DIR / "scripts" / "datetime_pipeline.py")]),
    ("Step 8", "Outlier Detection", [sys.executable, str(BASE_DIR / "scripts" / "outlier_detection.py")]),
    ("Step 9", "Validation Rules", [sys.executable, str(BASE_DIR / "scripts" / "validate_data_rules.py")]),
    ("Step 10", "Merge Validation", [sys.executable, str(BASE_DIR / "scripts" / "merge_validation.py")]),
    ("Step 11", "Feature Engineering", [sys.executable, str(BASE_DIR / "scripts" / "feature_engineering.py")]),
    ("Step 12", "Correlation Analysis", [sys.executable, str(BASE_DIR / "scripts" / "correlation_analysis.py")]),
    ("Step 13", "Segment Analysis", [sys.executable, str(BASE_DIR / "scripts" / "segment_analysis.py")]),
    ("Step 14", "Time-Series Analysis", [sys.executable, str(BASE_DIR / "scripts" / "time_series_analysis.py")]),
    ("Step 15", "Behavioral Analysis", [sys.executable, str(BASE_DIR / "scripts" / "behavioral_analysis.py")]),
    ("Step 16", "Funnel Analysis", [sys.executable, str(BASE_DIR / "scripts" / "funnel_analysis.py")]),
    ("Step 17", "KPI Analysis", [sys.executable, str(BASE_DIR / "scripts" / "kpi_analysis.py")]),
    ("Step 18", "Root Cause Analysis", [sys.executable, str(BASE_DIR / "scripts" / "root_cause_analysis.py")]),
    ("Step 19", "Deduplication", [sys.executable, str(BASE_DIR / "scripts" / "deduplication.py")]),
]

for label, title, command in extra_steps:
    print(f"\n{label} : {title}")
    subprocess.run(command, cwd=str(BASE_DIR), check=True)

print("\nPipeline Completed Successfully!")
