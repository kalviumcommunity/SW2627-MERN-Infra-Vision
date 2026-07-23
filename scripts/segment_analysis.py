import json
import os
from pathlib import Path

import pandas as pd

INPUT_FILE = "output/feature_engineered_data.csv"
SUMMARY_FILE = "output/segment_analysis_summary.csv"
REPORT_FILE = "output/segment_analysis_report.json"


def build_segment_analysis(df: pd.DataFrame):
    analysis_df = df.copy()

    if "CloudService" not in analysis_df.columns:
        analysis_df["CloudService"] = "Unknown"
    if "ProjectID" not in analysis_df.columns:
        analysis_df["ProjectID"] = [f"P{idx:03d}" for idx in range(1, len(analysis_df) + 1)]
    if "InfrastructureCost" not in analysis_df.columns:
        analysis_df["InfrastructureCost"] = 0.0
    if "CPUUsage" not in analysis_df.columns:
        analysis_df["CPUUsage"] = 0.0
    if "BillingID" not in analysis_df.columns:
        analysis_df["BillingID"] = range(1, len(analysis_df) + 1)

    service_summary = (
        analysis_df.groupby("CloudService")
        .agg(
            total_cost=("InfrastructureCost", "sum"),
            average_cpu=("CPUUsage", "mean"),
            project_count=("ProjectID", "count"),
            average_cost_per_project=("InfrastructureCost", "mean"),
        )
        .reset_index()
    )

    service_summary["cost_rank"] = service_summary["total_cost"].rank(ascending=False)
    service_summary["cpu_rank"] = service_summary["average_cpu"].rank(ascending=False)
    service_summary["cost_share"] = service_summary["total_cost"] / service_summary["total_cost"].sum()
    service_summary["opportunity_flag"] = service_summary["average_cpu"].gt(service_summary["average_cpu"].mean())

    multi_dim_summary = (
        analysis_df.groupby(["CloudService", "ProjectID"])
        .agg(
            total_cost=("InfrastructureCost", "sum"),
            average_cpu=("CPUUsage", "mean"),
            record_count=("BillingID", "count"),
        )
        .reset_index()
    )

    pivot_table = pd.pivot_table(
        analysis_df,
        values="InfrastructureCost",
        index="CloudService",
        columns="ProjectID",
        aggfunc="sum",
        fill_value=0,
    )

    analysis_df["avg_cpu_by_service"] = analysis_df.groupby("CloudService")["CPUUsage"].transform("mean")
    analysis_df["avg_cost_by_service"] = analysis_df.groupby("CloudService")["InfrastructureCost"].transform("mean")

    best_segment = service_summary.loc[service_summary["total_cost"].idxmax()]
    worst_segment = service_summary.loc[service_summary["average_cpu"].idxmax()]

    insights = [
        f"{best_segment['CloudService']} leads on total cost with {best_segment['total_cost']:.2f} and an average CPU of {best_segment['average_cpu']:.2f}.",
        f"{worst_segment['CloudService']} has the highest average CPU usage at {worst_segment['average_cpu']:.2f}, making it the main optimization target.",
        f"The segment summary contains {len(service_summary)} service groups and {len(multi_dim_summary)} project-level combinations.",
    ]

    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "segment_count": int(len(service_summary)),
        "insights": insights,
        "top_segment": {
            "name": str(best_segment["CloudService"]),
            "total_cost": float(best_segment["total_cost"]),
            "average_cpu": float(best_segment["average_cpu"]),
        },
        "priority_segment": {
            "name": str(worst_segment["CloudService"]),
            "average_cpu": float(worst_segment["average_cpu"]),
        },
        "summary_columns": list(service_summary.columns),
        "pivot_shape": list(pivot_table.shape),
    }

    return service_summary, multi_dim_summary, pivot_table, analysis_df, report


def main():
    if os.path.exists(INPUT_FILE):
        df = pd.read_csv(INPUT_FILE)
    else:
        df = pd.DataFrame(
            {
                "CloudService": ["AWS", "Azure", "GCP", "AWS"],
                "ProjectID": ["P001", "P002", "P003", "P004"],
                "InfrastructureCost": [1200, 1800, 900, 1400],
                "CPUUsage": [75, 82, 60, 79],
                "BillingID": [101, 102, 103, 104],
            }
        )

    service_summary, multi_dim_summary, pivot_table, analysis_df, report = build_segment_analysis(df)

    os.makedirs("output", exist_ok=True)
    service_summary.to_csv(SUMMARY_FILE, index=False)
    multi_dim_summary.to_csv("output/segment_analysis_multi_dim.csv", index=False)
    pivot_table.to_csv("output/segment_analysis_pivot.csv")
    analysis_df.to_csv("output/segment_analysis_augmented.csv", index=False)

    with open(REPORT_FILE, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print("=" * 60)
    print("GROUPBY AGGREGATION & SEGMENT INSIGHTS")
    print("=" * 60)
    print("Segment analysis completed")
    print(service_summary.to_string(index=False))
    print(f"Summary saved to: {SUMMARY_FILE}")
    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
