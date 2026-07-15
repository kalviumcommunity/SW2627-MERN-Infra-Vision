from pathlib import Path
import subprocess
import sys

print("=" * 60)
print("INFRAVISION DATA PIPELINE")
print("=" * 60)

BASE_DIR = Path(__file__).resolve().parent.parent

STEPS = [
	("Step 1", "Data Validation", [sys.executable, "-m", "scripts.validate_data"]),
	("Step 2", "Missing Value Imputation", [sys.executable, "-m", "scripts.missing_value_imputation"]),
	("Step 3", "NumPy Vectorized Computation", [sys.executable, "-m", "scripts.vectorized_computation"]),
	("Step 4", "Data Profiling", [sys.executable, "-m", "scripts.data_profiling"]),
	("Step 5", "Data Dictionary", [sys.executable, "-m", "scripts.data_dictionary"]),
]

for label, title, command in STEPS:
	print(f"\n{label} : {title}")
	subprocess.run(command, cwd=BASE_DIR, check=True)

print("\nPipeline Completed Successfully!")
