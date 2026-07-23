import json
import os

import pandas as pd

INPUT_FILE = "output/feature_engineered_data.csv"
FUNNEL_OUTPUT = "output/funnel_analysis.csv"
REPORT_FILE = "output/funnel_analysis_report.json"


def build_funnel_analysis(df: pd.DataFrame):
    analysis_df = df.copy()

    stage_columns = [
        "signup_completed",
        "email_verified",
        "payment_added",
        "first_purchase",
    ]

    for col in stage_columns:
        if col not in analysis_df.columns:
            analysis_df[col] = 0

    stages = {
        "Sign Up": int(analysis_df["signup_completed"].sum()),
        "Email Verified": int(analysis_df["email_verified"].sum()),
        "Payment Added": int(analysis_df["payment_added"].sum()),
        "First Purchase": int(analysis_df["first_purchase"].sum()),
    }

    stage_names = list(stages.keys())
    stage_values = list(stages.values())

    drop_off_rows = []
    for i in range(len(stage_values) - 1):
        lost = stage_values[i] - stage_values[i + 1]
        drop_rate = (lost / stage_values[i]) * 100 if stage_values[i] else 0.0
        drop_off_rows.append(
            {
                "from": stage_names[i],
                "to": stage_names[i + 1],
                "lost": lost,
                "drop_rate_pct": round(drop_rate, 2),
            }
        )

    funnel_df = pd.DataFrame(drop_off_rows)

    funnel_df["potential_recovery"] = funnel_df["lost"]
    funnel_df["priority_score"] = funnel_df["drop_rate_pct"] * funnel_df["lost"]

    biggest_leak = funnel_df.loc[funnel_df["drop_rate_pct"].idxmax()]

    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "stages": stages,
        "biggest_leak": {
            "from": str(biggest_leak["from"]),
            "to": str(biggest_leak["to"]),
            "lost": int(biggest_leak["lost"]),
            "drop_rate_pct": float(biggest_leak["drop_rate_pct"]),
        },
        "drop_off_table": funnel_df.to_dict(orient="records"),
    }

    return stages, funnel_df, report


def main():
    if os.path.exists(INPUT_FILE):
        df = pd.read_csv(INPUT_FILE)
    else:
        df = pd.DataFrame(
            {
                "signup_completed": [1, 1, 1, 1],
                "email_verified": [1, 1, 0, 0],
                "payment_added": [1, 0, 0, 0],
                "first_purchase": [1, 0, 0, 0],
            }
        )

    stages, funnel_df, report = build_funnel_analysis(df)

    os.makedirs("output", exist_ok=True)
    funnel_df.to_csv(FUNNEL_OUTPUT, index=False)

    with open(REPORT_FILE, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print("=" * 60)
    print("FUNNEL ANALYSIS & DROP-OFF DETECTION")
    print("=" * 60)
    print("Funnel analysis completed")
    print(pd.DataFrame([stages], index=["count"]).T.to_string())
    print(funnel_df.to_string(index=False))
    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
