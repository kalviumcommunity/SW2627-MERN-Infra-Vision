import os

print("=" * 60)
print("INFRAVISION DATA PIPELINE")
print("=" * 60)

print("\nStep 1 : Data Validation")
os.system("python scripts/validate_data.py")

print("\nStep 2 : Missing Value Imputation")
os.system("python scripts/missing_value_imputation.py")

print("\nStep 3 : Data Profiling")
os.system("python scripts/data_profiling.py")

print("\nStep 4 : Data Dictionary")
os.system("python scripts/data_dictionary.py")

print("\nStep 5 : String Cleaning")
os.system("python scripts/string_cleaning.py")

print("\nStep 6 : Date & Time Transformation")
os.system("python scripts/datetime_pipeline.py")

print("\nStep 7 : Outlier Detection")
os.system("python scripts/outlier_detection.py")

print("\nStep 8 : Deduplication")
os.system("python scripts/deduplication.py")

print("\nPipeline Completed Successfully!")
