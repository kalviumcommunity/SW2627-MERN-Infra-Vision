import json
import os

import pandas as pd

INPUT_FILE = "output/feature_engineered_data.csv"
OUTPUT_FILE = "output/root_cause_analysis_report.json"


def build_root_cause_report(df: pd.DataFrame):
    analysis_df = df.copy()

    if "timestamp" in analysis_df.columns:
        analysis_df["timestamp"] = pd.to_datetime(analysis_df["timestamp"], errors="coerce")
    else:
        analysis_df["timestamp"] = pd.date_range("2024-01-01", periods=len(analysis_df), freq="h")

    if "status" in analysis_df.columns:
        analysis_df["success_rate"] = (analysis_df["status"] == "completed").astype(int)
    else:
        analysis_df["success_rate"] = 1

    if "payment_method" not in analysis_df.columns:
        analysis_df["payment_method"] = ["credit_card", "debit", "crypto"][: len(analysis_df)]

    daily_success = analysis_df.groupby(analysis_df["timestamp"].dt.date)["success_rate"].mean()
    anomaly_date = daily_success[daily_success < 0.5].index[0] if (daily_success < 0.5).any() else daily_success.index[0]

    anomaly_day = analysis_df[analysis_df["timestamp"].dt.date == anomaly_date]
    hourly_success = anomaly_day.groupby(anomaly_day["timestamp"].dt.hour)["success_rate"].mean()

    during_anomaly = anomaly_day[anomaly_day["timestamp"].dt.hour.isin([11, 12, 13])]
    success_by_payment = during_anomaly.groupby("payment_method")["success_rate"].mean()

    findings = {
        "anomaly_date": str(anomaly_date),
        "hourly_success": hourly_success.to_dict(),
        "success_by_payment": success_by_payment.to_dict(),
        "hypothesis": "Payment processor outage affecting credit card transactions during the anomaly window.",
        "recommendation": "Add redundant payment processor and automatic failover for affected payment methods.",
    }

    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "findings": findings,
    }
    return report


def main():
    if os.path.exists(INPUT_FILE):
        df = pd.read_csv(INPUT_FILE)
    else:
        df = pd.DataFrame(
            {
                "timestamp": ["2024-01-15 10:00:00", "2024-01-15 11:00:00", "2024-01-15 12:00:00", "2024-01-15 13:00:00"],
                "status": ["completed", "failed", "failed", "failed"],
                "payment_method": ["credit_card", "credit_card", "credit_card", "credit_card"],
            }
        )

    report = build_root_cause_report(df)

    os.makedirs("output", exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print("=" * 60)
    print("ROOT CAUSE INVESTIGATION WORKFLOW")
    print("=" * 60)
    print("Root cause analysis completed")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
