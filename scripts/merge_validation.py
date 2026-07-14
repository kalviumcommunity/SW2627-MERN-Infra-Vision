import json
import os

import pandas as pd

LEFT_FILE = "data/raw/customers.csv"
RIGHT_FILE = "data/raw/orders.csv"
OUTPUT_FILE = "output/merged_data.csv"
UNMATCHED_LEFT_FILE = "output/unmatched_customers.csv"
UNMATCHED_RIGHT_FILE = "output/unmatched_orders.csv"
REPORT_FILE = "output/merge_validation_report.json"


def load_inputs():
    if os.path.exists(LEFT_FILE) and os.path.exists(RIGHT_FILE):
        left_df = pd.read_csv(LEFT_FILE)
        right_df = pd.read_csv(RIGHT_FILE)
    else:
        left_df = pd.DataFrame({"customer_id": [101, 102, 103], "customer_name": ["Alice", "Bob", "Charlie"]})
        right_df = pd.DataFrame({"customer_id": [101, 103, 104], "order_value": [100, 200, 300]})
    return left_df, right_df


def validate_merge(left_df: pd.DataFrame, right_df: pd.DataFrame):
    left_rows = len(left_df)
    right_rows = len(right_df)

    join_key = "customer_id"
    if join_key not in left_df.columns:
        join_key = next((col for col in left_df.columns if col.lower() == "customer_id"), None)
    if join_key is None:
        raise ValueError("No customer_id column found in left dataset")

    if join_key not in right_df.columns:
        right_key = next((col for col in right_df.columns if col.lower() == "customer_id"), None)
        if right_key is None:
            raise ValueError("No customer_id column found in right dataset")
    else:
        right_key = join_key

    merged_df = pd.merge(left_df, right_df, left_on=join_key, right_on=right_key, how="left", indicator=True)

    unmatched_left = left_df[~left_df[join_key].isin(right_df[right_key])]
    unmatched_right = right_df[~right_df[right_key].isin(left_df[join_key])]

    report = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "join_type": "left",
        "left_rows": left_rows,
        "right_rows": right_rows,
        "merged_rows": len(merged_df),
        "row_change": len(merged_df) - left_rows,
        "unmatched_left_rows": len(unmatched_left),
        "unmatched_right_rows": len(unmatched_right),
        "notes": "Left join used to preserve left-table records and validate unmatched right-side keys.",
    }

    return merged_df, unmatched_left, unmatched_right, report


def main():
    left_df, right_df = load_inputs()
    merged_df, unmatched_left, unmatched_right, report = validate_merge(left_df, right_df)

    os.makedirs("output", exist_ok=True)
    merged_df.to_csv(OUTPUT_FILE, index=False)
    unmatched_left.to_csv(UNMATCHED_LEFT_FILE, index=False)
    unmatched_right.to_csv(UNMATCHED_RIGHT_FILE, index=False)

    with open(REPORT_FILE, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print("=" * 60)
    print("MULTI-SOURCE MERGING AND JOIN VALIDATION")
    print("=" * 60)
    print(f"Left rows: {report['left_rows']}")
    print(f"Right rows: {report['right_rows']}")
    print(f"Merged rows: {report['merged_rows']}")
    print(f"Row change: {report['row_change']}")
    print(f"Unmatched left rows: {report['unmatched_left_rows']}")
    print(f"Unmatched right rows: {report['unmatched_right_rows']}")
    print(f"Merged data saved to: {OUTPUT_FILE}")
    print(f"Unmatched left saved to: {UNMATCHED_LEFT_FILE}")
    print(f"Unmatched right saved to: {UNMATCHED_RIGHT_FILE}")
    print(f"Report saved to: {REPORT_FILE}")


if __name__ == "__main__":
    main()
