import json
import os

import pandas as pd

INPUT_FILE = "output/segment_analysis_augmented.csv"
ROLLING_OUTPUT = "output/time_series_trends.csv"
REPORT_FILE = "output/time_series_report.json"


def build_time_series_analysis(df: pd.DataFrame):
    analysis_df = df.copy()

    if "date" in analysis_df.columns:
        analysis_df["date"] = pd.to_datetime(analysis_df["date"], errors="coerce")
    else:
        analysis_df["date"] = pd.date_range(start="2024-01-01", periods=len(analysis_df), freq="D")

    if "revenue" in analysis_df.columns:
        analysis_df["revenue"] = pd.to_numeric(analysis_df["revenue"], errors="coerce")
    elif "InfrastructureCost" in analysis_df.columns:
        analysis_df["revenue"] = pd.to_numeric(analysis_df["InfrastructureCost"], errors="coerce")
    else:
        analysis_df["revenue"] = 0.0

    analysis_df = analysis_df.sort_values("date").reset_index(drop=True)
    analysis_df["revenue_ma7"] = analysis_df["revenue"].rolling(window=7, min_periods=1).mean()
    analysis_df["revenue_ma30"] = analysis_df["revenue"].rolling(window=30, min_periods=1).mean()
    analysis_df["cumulative_revenue"] = analysis_df["revenue"].cumsum()
    analysis_df["daily_change_pct"] = analysis_df["revenue"].pct_change() * 100

    monthly_revenue = analysis_df.set_index("date")["revenue"].resample("ME").sum()
    monthly_change_pct = monthly_revenue.pct_change() * 100
    monthly_summary = pd.DataFrame({
        "monthly_revenue": monthly_revenue,
        "monthly_change_pct": monthly_change_pct,
    }).reset_index()

    monthly_summary = monthly_summary.rename(columns={"date": "month"})

    last_value = monthly_summary["monthly_revenue"].iloc[-1] if not monthly_summary.empty else 0.0
    prev_value = monthly_summary["monthly_revenue"].iloc[-2] if len(monthly_summary) > 1 else 0.0
    if last_value > prev_value:
        trend_label = "uptrend"
    elif last_value < prev_value:
        trend_label = "downtrend"
    else:
        trend_label = "flat"

    rolling_change = analysis_df["revenue_ma7"].pct_change() * 100
    inflection_points = []
    for idx, value in enumerate(rolling_change.iloc[1:], start=1):
        if pd.notna(value) and value > 5:
            inflection_points.append({"index": int(idx), "date": analysis_df.loc[idx, "date"].strftime("%Y-%m-%d"), "change_pct": round(float(value), 2)})

    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "row_count": int(len(analysis_df)),
        "trend_label": trend_label,
        "latest_monthly_revenue": float(last_value),
        "latest_monthly_change_pct": float(monthly_summary["monthly_change_pct"].iloc[-1]) if not monthly_summary.empty else 0.0,
        "rolling_window": 7,
        "inflection_points": inflection_points[:5],
        "summary_columns": list(monthly_summary.columns),
    }

    return analysis_df, monthly_summary, report


def main():
    if os.path.exists(INPUT_FILE):
        df = pd.read_csv(INPUT_FILE)
    else:
        df = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=6, freq="D"),
            "InfrastructureCost": [1200, 1400, 1600, 1500, 1650, 1800],
        })

    analysis_df, monthly_summary, report = build_time_series_analysis(df)

    os.makedirs("output", exist_ok=True)
    analysis_df.to_csv(ROLLING_OUTPUT, index=False)
    monthly_summary.to_csv("output/time_series_monthly_summary.csv", index=False)

    with open(REPORT_FILE, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print("=" * 60)
    print("TIME-SERIES TREND & ROLLING METRICS")
    print("=" * 60)
    print("Time-series analysis completed")
    print(analysis_df[["date", "revenue", "revenue_ma7", "cumulative_revenue", "daily_change_pct"]].head(10).to_string(index=False))
    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
