# InfraVision

## Project Overview
InfraVision is a data engineering project that validates, cleans, profiles, and documents cloud infrastructure billing data.

## Features
- Data Validation
- Missing Value Imputation
- Data Profiling
- Data Dictionary Generation

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

- intake_report.json
- processed_cloud_data.csv
- data_profile_report.txt
- data_dictionary.csv
