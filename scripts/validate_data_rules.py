import json
import os
import re

import pandas as pd

INPUT_FILE = "output/processed_cloud_data.csv"
OUTPUT_FILE = "output/processed_cloud_data.csv"
FAILURES_FILE = "output/validation_failures.csv"
REPORT_FILE = "output/validation_report.json"


def validate_dataframe(df: pd.DataFrame):
    validation_results = []
    validated_df = df.copy()

    if "BillingID" in validated_df.columns:
        valid_billing = validated_df["BillingID"].notna() & (validated_df["BillingID"] > 0)
        validation_results.append({
            "rule": "BillingID is present and positive",
            "passed": int(valid_billing.sum()),
            "failed": int((~valid_billing).sum()),
            "status": "pass" if (~valid_billing).sum() == 0 else "fail",
        })
        validated_df["valid_billing_id"] = valid_billing.astype(int)

    if "InfrastructureCost" in validated_df.columns:
        valid_cost = validated_df["InfrastructureCost"].notna() & (validated_df["InfrastructureCost"] >= 0)
        validation_results.append({
            "rule": "InfrastructureCost is non-negative",
            "passed": int(valid_cost.sum()),
            "failed": int((~valid_cost).sum()),
            "status": "pass" if (~valid_cost).sum() == 0 else "fail",
        })
        validated_df["valid_infrastructure_cost"] = valid_cost.astype(int)

    if "CPUUsage" in validated_df.columns:
        valid_cpu = validated_df["CPUUsage"].notna() & (validated_df["CPUUsage"] >= 0) & (validated_df["CPUUsage"] <= 100)
        validation_results.append({
            "rule": "CPUUsage is between 0 and 100",
            "passed": int(valid_cpu.sum()),
            "failed": int((~valid_cpu).sum()),
            "status": "pass" if (~valid_cpu).sum() == 0 else "fail",
        })
        validated_df["valid_cpu_usage"] = valid_cpu.astype(int)

    if "CloudService" in validated_df.columns:
        valid_service = validated_df["CloudService"].notna() & validated_df["CloudService"].astype(str).str.strip().str.len().gt(0)
        validation_results.append({
            "rule": "CloudService is not empty",
            "passed": int(valid_service.sum()),
            "failed": int((~valid_service).sum()),
            "status": "pass" if (~valid_service).sum() == 0 else "fail",
        })
        validated_df["valid_cloud_service"] = valid_service.astype(int)

    if {"BillingID", "ProjectID"}.issubset(validated_df.columns):
        valid_reference = validated_df["ProjectID"].notna() & validated_df["BillingID"].notna()
        validation_results.append({
            "rule": "BillingID and ProjectID are present together",
            "passed": int(valid_reference.sum()),
            "failed": int((~valid_reference).sum()),
            "status": "pass" if (~valid_reference).sum() == 0 else "fail",
        })
        validated_df["valid_reference_pair"] = valid_reference.astype(int)

    rule_columns = [col for col in validated_df.columns if col.startswith("valid_")]
    if rule_columns:
        validated_df["passes_all_checks"] = validated_df[rule_columns].all(axis=1).astype(int)
        failures = validated_df[validated_df["passes_all_checks"] == 0]
        failures.to_csv(FAILURES_FILE, index=False)
    else:
        failures = validated_df.iloc[0:0]

    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "records": int(len(validated_df)),
        "passed": int(validated_df["passes_all_checks"].sum()) if "passes_all_checks" in validated_df.columns else int(len(validated_df)),
        "failed": int(len(validated_df) - (validated_df["passes_all_checks"].sum() if "passes_all_checks" in validated_df.columns else len(validated_df))),
        "rules": validation_results,
    }

    return validated_df, failures, report


def main():
    df = pd.read_csv(INPUT_FILE)
    validated_df, failures, report = validate_dataframe(df)

    os.makedirs("output", exist_ok=True)
    validated_df.to_csv(OUTPUT_FILE, index=False)

    with open(REPORT_FILE, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print("=" * 60)
    print("DATA CONSISTENCY AND VALIDATION RULES")
    print("=" * 60)
    print(f"Records: {report['records']}")
    print(f"Passed: {report['passed']}")
    print(f"Failed: {report['failed']}")
    print(f"Failures saved to: {FAILURES_FILE}")
    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
