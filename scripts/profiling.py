import csv
import json
from pathlib import Path
from typing import Any

import pandas as pd


def profile_nulls_and_duplicates(df: pd.DataFrame) -> dict[str, Any]:
    total_rows = len(df)
    profile: dict[str, Any] = {}

    for col in df.columns:
        series = df[col]
        null_count = int(series.isna().sum())
        null_pct = round(null_count * 100 / total_rows, 2) if total_rows else 0.0
        distinct_count = int(series.nunique(dropna=True))
        value_counts = series.value_counts(dropna=True).head(10)
        top_values = [
            {
                "value": value if pd.notna(value) else None,
                "count": int(count),
                "pct": round(int(count) * 100 / max(total_rows - null_count, 1), 2),
            }
            for value, count in value_counts.items()
        ]

        profile[col] = {
            "dtype": str(series.dtype),
            "null_count": null_count,
            "null_pct": null_pct,
            "distinct_count": distinct_count,
            "top_values": top_values,
        }

    exact_duplicates = int(df.duplicated().sum())
    duplicate_pct = round(exact_duplicates * 100 / total_rows, 2) if total_rows else 0.0

    profile["_summary"] = {
        "rows": total_rows,
        "columns": len(df.columns),
        "exact_duplicates": exact_duplicates,
        "duplicate_pct": duplicate_pct,
    }

    return profile


def profile_numerical(df: pd.DataFrame) -> dict[str, Any]:
    summary: dict[str, Any] = {}

    for col in df.select_dtypes(include=["number"]).columns:
        series = df[col]
        clean = series.dropna()
        count = int(clean.count())
        null_count = int(series.isna().sum())
        negative_count = int((clean < 0).sum())
        zero_count = int((clean == 0).sum())

        summary[col] = {
            "dtype": str(series.dtype),
            "count": count,
            "null_count": null_count,
            "min": clean.min() if count else None,
            "max": clean.max() if count else None,
            "mean": round(clean.mean(), 2) if count else None,
            "median": round(clean.median(), 2) if count else None,
            "std": round(clean.std(), 2) if count else None,
            "25%": round(clean.quantile(0.25), 2) if count else None,
            "75%": round(clean.quantile(0.75), 2) if count else None,
            "negative_count": negative_count,
            "zero_count": zero_count,
            "negative_pct": round(negative_count * 100 / count, 2) if count else 0.0,
        }

    return summary


def profile_categorical(df: pd.DataFrame, top_n: int = 10) -> dict[str, Any]:
    summary: dict[str, Any] = {}

    for col in df.select_dtypes(include=["object", "category", "bool"]).columns:
        series = df[col]
        null_count = int(series.isna().sum())
        top_values = series.value_counts(dropna=True).head(top_n)
        summary[col] = {
            "dtype": str(series.dtype),
            "count": int(series.count()),
            "null_count": null_count,
            "distinct_count": int(series.nunique(dropna=True)),
            "top_values": [
                {
                    "value": value if pd.notna(value) else None,
                    "count": int(count),
                    "pct": round(int(count) * 100 / max(len(series) - null_count, 1), 2),
                }
                for value, count in top_values.items()
            ],
        }

    return summary


def identify_issues(df: pd.DataFrame, null_threshold: float = 30.0, dup_threshold: float = 5.0) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    total_rows = len(df)

    for col in df.columns:
        null_count = int(df[col].isna().sum())
        null_pct = round(null_count * 100 / total_rows, 2) if total_rows else 0.0
        if null_pct > null_threshold:
            issues.append(
                {
                    "column": col,
                    "type": "High nulls",
                    "value": f"{null_pct:.1f}%",
                    "detail": f"{null_count} null values out of {total_rows} rows",
                }
            )

    exact_duplicates = int(df.duplicated().sum())
    duplicate_pct = round(exact_duplicates * 100 / total_rows, 2) if total_rows else 0.0
    if duplicate_pct > dup_threshold:
        issues.append(
            {
                "column": None,
                "type": "High duplicates",
                "value": f"{duplicate_pct:.1f}%",
                "detail": f"{exact_duplicates} exact duplicate rows detected",
            }
        )

    for col in df.select_dtypes(include=["number"]).columns:
        numeric = df[col].dropna()
        if numeric.empty:
            continue
        negative_count = int((numeric < 0).sum())
        if negative_count:
            issues.append(
                {
                    "column": col,
                    "type": "Negative values",
                    "value": negative_count,
                    "detail": f"{negative_count} negative values found in numeric column",
                }
            )

    return issues


def profile_dataframe(df: pd.DataFrame, null_threshold: float = 30.0, dup_threshold: float = 5.0) -> dict[str, Any]:
    return {
        "summary": profile_nulls_and_duplicates(df),
        "numerical": profile_numerical(df),
        "categorical": profile_categorical(df),
        "issues": identify_issues(df, null_threshold, dup_threshold),
    }


def save_profile_report(report: dict[str, Any], filepath: str) -> None:
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, default=str)


def save_issues_report(issues: list[dict[str, Any]], filepath: str) -> None:
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["column", "type", "value", "detail"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for issue in issues:
            writer.writerow({k: issue.get(k, "") for k in fieldnames})


def print_profile_summary(report: dict[str, Any]) -> None:
    summary = report.get("summary", {}).get("_summary", {})
    issues = report.get("issues", [])

    print("\n====== DATA PROFILING SUMMARY ======")
    print(f"Rows: {summary.get('rows', 0)}")
    print(f"Columns: {summary.get('columns', 0)}")
    print(f"Exact duplicates: {summary.get('exact_duplicates', 0)}")
    print(f"Duplicate pct: {summary.get('duplicate_pct', 0.0)}%")
    print(f"Detected issues: {len(issues)}")

    if issues:
        print("\nTop issues:")
        for issue in issues[:10]:
            column = issue.get("column") or "[dataset]"
            print(f"- {issue['type']} ({column}): {issue['value']} - {issue['detail']}")

    print("\n === Column nulls and value distributions are available in the saved profile report ===")
