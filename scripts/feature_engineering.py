import json
import os

import pandas as pd

INPUT_FILE = "output/merged_data.csv"
OUTPUT_FILE = "output/feature_engineered_data.csv"
REPORT_FILE = "output/feature_engineering_report.json"


def engineer_features(df: pd.DataFrame):
    engineered_df = df.copy()

    if {"total_transactions", "days_as_customer"}.issubset(engineered_df.columns):
        engineered_df["transactions_per_month"] = engineered_df["total_transactions"] / (engineered_df["days_as_customer"] / 30)
    elif {"total_transactions", "days_as_customer"}.issubset(engineered_df.columns) is False:
        engineered_df["transactions_per_month"] = 0.0

    if {"total_spent", "total_transactions"}.issubset(engineered_df.columns):
        engineered_df["avg_spend_per_transaction"] = engineered_df["total_spent"] / engineered_df["total_transactions"].replace(0, pd.NA)
    else:
        engineered_df["avg_spend_per_transaction"] = 0.0

    if "transactions_per_month" in engineered_df.columns:
        engineered_df["engagement_tier"] = pd.cut(
            engineered_df["transactions_per_month"],
            bins=[-float("inf"), 2, 10, float("inf")],
            labels=["low", "medium", "high"],
            include_lowest=True,
        )

    if "total_spent" in engineered_df.columns:
        engineered_df["spend_tier"] = pd.qcut(
            engineered_df["total_spent"].fillna(0),
            q=4,
            labels=["tier_1", "tier_2", "tier_3", "tier_4"],
            duplicates="drop",
        )

    if {"days_since_last_purchase", "total_transactions", "total_spent"}.issubset(engineered_df.columns):
        engineered_df["recency_score"] = pd.qcut(engineered_df["days_since_last_purchase"].fillna(0), q=5, labels=[5, 4, 3, 2, 1], duplicates="drop")
        engineered_df["frequency_score"] = pd.qcut(engineered_df["total_transactions"].fillna(0), q=5, labels=[1, 2, 3, 4, 5], duplicates="drop")
        engineered_df["monetary_score"] = pd.qcut(engineered_df["total_spent"].fillna(0), q=5, labels=[1, 2, 3, 4, 5], duplicates="drop")
        engineered_df["rfm_score"] = (
            engineered_df["recency_score"].astype(int)
            + engineered_df["frequency_score"].astype(int)
            + engineered_df["monetary_score"].astype(int)
        )

    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "features_created": [
            col for col in ["transactions_per_month", "avg_spend_per_transaction", "engagement_tier", "spend_tier", "rfm_score"] if col in engineered_df.columns
        ],
    }

    return engineered_df, report


def main():
    if os.path.exists(INPUT_FILE):
        df = pd.read_csv(INPUT_FILE)
    else:
        df = pd.DataFrame({"total_transactions": [5], "days_as_customer": [180], "total_spent": [100], "days_since_last_purchase": [10]})

    engineered_df, report = engineer_features(df)

    os.makedirs("output", exist_ok=True)
    engineered_df.to_csv(OUTPUT_FILE, index=False)

    with open(REPORT_FILE, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print("=" * 60)
    print("FEATURE ENGINEERING AND DERIVED BUSINESS COLUMNS")
    print("=" * 60)
    print("Feature engineering completed")
    print(f"Features created: {', '.join(report['features_created'])}")
    print(f"Output saved to: {OUTPUT_FILE}")
    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
