import json
import os

import pandas as pd

INPUT_FILE = "output/feature_engineered_data.csv"
OUTPUT_FILE = "output/kpi_metrics.csv"
REPORT_FILE = "output/kpi_analysis_report.json"


def calculate_active_customers(df: pd.DataFrame, days: int = 30) -> int:
    if "transaction_date" in df.columns:
        df = df.copy()
        df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
        cutoff = pd.Timestamp.now().normalize() - pd.Timedelta(days=days)
        active = df[df["transaction_date"] >= cutoff]["customer_id"].dropna().nunique() if "customer_id" in df.columns else 0
    else:
        active = 0
    return int(active)


def calculate_revenue_per_customer(df: pd.DataFrame) -> float:
    if "amount" in df.columns and "customer_id" in df.columns:
        total_revenue = pd.to_numeric(df["amount"], errors="coerce").sum()
        unique_customers = df["customer_id"].dropna().nunique()
        return float(total_revenue / unique_customers) if unique_customers else 0.0
    return 0.0


def calculate_churn_rate(df: pd.DataFrame) -> float:
    if "churn" in df.columns:
        return float(pd.to_numeric(df["churn"], errors="coerce").mean())
    return 0.0


def build_kpi_report(df: pd.DataFrame):
    active_customers = calculate_active_customers(df)
    revenue_per_customer = calculate_revenue_per_customer(df)
    churn_rate = calculate_churn_rate(df)

    kpi_rows = [
        {
            "kpi_name": "Active Customers",
            "formula": "Distinct customer_id with transaction_date in the last 30 days",
            "value": active_customers,
            "target_min": 5,
            "target_max": 10,
            "status": "pass" if 5 <= active_customers <= 10 else "out_of_range",
        },
        {
            "kpi_name": "Revenue per Customer",
            "formula": "Total amount / distinct customer_id",
            "value": round(revenue_per_customer, 2),
            "target_min": 100,
            "target_max": 500,
            "status": "pass" if 100 <= revenue_per_customer <= 500 else "out_of_range",
        },
        {
            "kpi_name": "Churn Rate",
            "formula": "Mean churn column",
            "value": round(churn_rate, 4),
            "target_min": 0.0,
            "target_max": 0.05,
            "status": "pass" if 0.0 <= churn_rate <= 0.05 else "out_of_range",
        },
    ]

    kpi_df = pd.DataFrame(kpi_rows)
    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "kpis": kpi_rows,
        "summary": {
            "passed": int((kpi_df["status"] == "pass").sum()),
            "failed": int((kpi_df["status"] != "pass").sum()),
        },
    }
    return kpi_df, report


def main():
    if os.path.exists(INPUT_FILE):
        df = pd.read_csv(INPUT_FILE)
    else:
        df = pd.DataFrame(
            {
                "customer_id": [1, 2, 3, 4],
                "transaction_date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
                "amount": [120, 180, 140, 160],
                "churn": [0.01, 0.02, 0.03, 0.02],
            }
        )

    kpi_df, report = build_kpi_report(df)

    os.makedirs("output", exist_ok=True)
    kpi_df.to_csv(OUTPUT_FILE, index=False)

    with open(REPORT_FILE, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print("=" * 60)
    print("KPI DEFINITION & BUSINESS METRIC DESIGN")
    print("=" * 60)
    print("KPI analysis completed")
    print(kpi_df.to_string(index=False))
    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
