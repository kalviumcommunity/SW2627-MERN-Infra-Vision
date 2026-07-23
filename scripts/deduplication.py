import json
import os
from datetime import datetime

import pandas as pd

INPUT_FILE = "output/processed_cloud_data.csv"
OUTPUT_FILE = "output/processed_cloud_data.csv"
AUDIT_FILE = "output/removed_duplicates_audit.csv"
SUMMARY_FILE = "output/deduplication_summary.json"


def select_key_columns(df: pd.DataFrame):
    preferred = [
        "BillingID",
        "ProjectID",
        "CustomerID",
        "customer_id",
        "transaction_id",
        "transaction_date",
        "date",
    ]
    available = [col for col in preferred if col in df.columns]
    if available:
        return available[:2]

    for col in df.columns:
        lower = col.lower()
        if any(token in lower for token in ["id", "code", "number"]):
            return [col]

    return []


def build_completeness_score(row: pd.Series, columns):
    return int(row[columns].notna().sum())


def deduplicate_dataframe(df: pd.DataFrame, key_columns=None):
    original_df = df.copy().reset_index(drop=True)
    original_df["__original_order"] = range(len(original_df))

    exact_mask = original_df.duplicated(keep="first")
    removal_mask = exact_mask.copy()
    removed_rows = []

    key_columns = key_columns or select_key_columns(original_df)

    if key_columns:
        for _, group in original_df.groupby(key_columns, dropna=False):
            if len(group) <= 1:
                continue

            non_key_columns = [
                col
                for col in original_df.columns
                if col not in key_columns and col not in ["__original_order"]
            ]
            if not non_key_columns:
                continue

            distinct_values = group[non_key_columns].drop_duplicates()
            if len(distinct_values) <= 1:
                continue

            group = group.copy()
            group["__completeness"] = group[non_key_columns].apply(
                lambda row: build_completeness_score(row, non_key_columns), axis=1
            )
            best_idx = group.sort_values(
                ["__completeness", "__original_order"], ascending=[False, True]
            ).index[0]

            for idx in group.index:
                if idx == best_idx:
                    continue
                if not removal_mask.loc[idx]:
                    removal_mask.loc[idx] = True
                removed_rows.append(
                    {
                        "row_index": int(idx),
                        "reason": "near_duplicate",
                        "kept_row_index": int(best_idx),
                        "key_columns": key_columns,
                        "key_values": {
                            col: original_df.loc[idx, col] for col in key_columns if col in original_df.columns
                        },
                    }
                )

    deduped_df = original_df.loc[~removal_mask].copy()
    deduped_df = deduped_df.drop(columns=["__original_order", "__completeness"], errors="ignore")

    for idx in original_df.index[exact_mask & ~removal_mask]:
        removed_rows.append(
            {
                "row_index": int(idx),
                "reason": "exact_duplicate",
                "kept_row_index": int(idx),
                "key_columns": key_columns,
                "key_values": {
                    col: original_df.loc[idx, col] for col in key_columns if col in key_columns
                },
            }
        )

    removed_df = pd.DataFrame(removed_rows)
    if not removed_df.empty:
        removed_df = removed_df.drop_duplicates(subset=["row_index", "reason"], keep="first")

    near_duplicate_count = int(
        removed_df[removed_df["reason"] == "near_duplicate"].shape[0]
    ) if not removed_df.empty and "reason" in removed_df.columns else 0

    summary = {
        "timestamp": datetime.now().isoformat(),
        "rows_before": int(len(original_df)),
        "rows_after": int(len(deduped_df)),
        "rows_removed": int(len(original_df) - len(deduped_df)),
        "removal_pct": round((len(original_df) - len(deduped_df)) * 100 / len(original_df), 2) if len(original_df) else 0.0,
        "exact_duplicates": int(exact_mask.sum()),
        "near_duplicates": near_duplicate_count,
        "strategy": "keep the first exact duplicate and the most complete record for near-duplicates",
        "key_columns": key_columns,
    }

    return deduped_df, removed_df, summary


def main():
    if os.path.exists(INPUT_FILE):
        df = pd.read_csv(INPUT_FILE)
    else:
        df = pd.read_csv("data/raw/cloud_data.csv")

    os.makedirs("output", exist_ok=True)

    deduped_df, removed_df, summary = deduplicate_dataframe(df)

    deduped_df.to_csv(OUTPUT_FILE, index=False)

    if removed_df.empty:
        removed_df.to_csv(AUDIT_FILE, index=False)
    else:
        removed_df.to_csv(AUDIT_FILE, index=False)

    with open(SUMMARY_FILE, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    print("=" * 60)
    print("DUPLICATE DETECTION AND REMOVAL")
    print("=" * 60)
    print(f"Rows before: {summary['rows_before']}")
    print(f"Rows after: {summary['rows_after']}")
    print(f"Rows removed: {summary['rows_removed']}")
    print(f"Removal percentage: {summary['removal_pct']}%")
    print(f"Exact duplicates detected: {summary['exact_duplicates']}")
    print(f"Near duplicates detected: {summary['near_duplicates']}")
    print(f"Audit trail saved to: {AUDIT_FILE}")
    print(f"Summary saved to: {SUMMARY_FILE}")


if __name__ == "__main__":
    main()
