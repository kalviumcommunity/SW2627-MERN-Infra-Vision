# InfraVision

## Project Overview
InfraVision is a data engineering project that validates, cleans, profiles, and documents cloud infrastructure billing data.

## Features
- Data Validation
- Missing Value Imputation
- Data Profiling
- Data Dictionary Generation
- Duplicate Detection and Removal with Audit Trail
- String Cleaning and Text Normalisation
- Date & Time Transformation Pipeline
- Outlier Detection with Statistical Methods

## Project Structure

```
data/
output/
scripts/
main.py
requirements.txt
README.md
```

## Run the Project

```bash
python scripts/workflow.py
streamlit run main.py
```

## Output Files

- output/intake_report.json
- output/processed_cloud_data.csv
- output/data_profile_report.txt
- output/data_dictionary.csv
- output/removed_duplicates_audit.csv
- output/deduplication_summary.json
