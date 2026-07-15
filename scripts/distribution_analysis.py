import json

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import gaussian_kde

try:
    from .common import DISTRIBUTION_DIR, DISTRIBUTION_REPORT_FILE, PROCESSED_DATA_FILE, ensure_distribution_dir, load_csv
except ImportError:
    from common import DISTRIBUTION_DIR, DISTRIBUTION_REPORT_FILE, PROCESSED_DATA_FILE, ensure_distribution_dir, load_csv


def describe_distribution(series):
    clean = series.dropna().astype(float)

    if clean.empty:
        return {
            "count": 0,
            "min": None,
            "max": None,
            "mean": None,
            "median": None,
            "skewness": None,
            "kurtosis": None,
            "interpretation": "No numeric values available.",
        }

    skewness = float(stats.skew(clean, bias=False)) if len(clean) > 2 else 0.0
    kurtosis = float(stats.kurtosis(clean, bias=False)) if len(clean) > 3 else 0.0
    median = float(clean.median())
    mean = float(clean.mean())

    if abs(skewness) > 1:
        skew_note = "highly skewed"
    elif abs(skewness) > 0.5:
        skew_note = "moderately skewed"
    else:
        skew_note = "roughly symmetric"

    if kurtosis > 3:
        tail_note = "heavy-tailed with likely outliers"
    elif kurtosis < 0:
        tail_note = "light-tailed and relatively concentrated"
    else:
        tail_note = "close to normal tail weight"

    if abs(mean - median) / max(abs(median), 1.0) > 0.1:
        center_note = "mean and median differ enough that the median is more representative"
    else:
        center_note = "mean and median are close, so the average is reasonably representative"

    interpretation = f"The distribution is {skew_note}, {tail_note}, and {center_note}."

    return {
        "count": int(clean.count()),
        "min": float(clean.min()),
        "max": float(clean.max()),
        "mean": mean,
        "median": median,
        "skewness": skewness,
        "kurtosis": kurtosis,
        "interpretation": interpretation,
    }


def save_histogram_and_kde(series, column_name):
    clean = series.dropna().astype(float)
    if clean.empty:
        return None

    x_values = np.linspace(clean.min(), clean.max(), 200)
    density = None
    if len(clean.unique()) > 1:
        density = gaussian_kde(clean)(x_values)

    figure, axis = plt.subplots(figsize=(10, 5))
    axis.hist(clean, bins=30, density=True, alpha=0.6, edgecolor="black", label="Histogram")
    if density is not None:
        axis.plot(x_values, density, linewidth=2, label="KDE")

    axis.set_title(f"{column_name} Distribution")
    axis.set_xlabel(column_name)
    axis.set_ylabel("Density")
    axis.legend()
    figure.tight_layout()

    output_path = DISTRIBUTION_DIR / f"{column_name.lower()}_distribution.png"
    figure.savefig(output_path, dpi=150)
    plt.close(figure)
    return output_path


def save_segment_comparison(df, column_name):
    series = df[column_name].dropna().astype(float)
    if series.empty:
        return None

    low_cutoff = series.quantile(0.25)
    high_cutoff = series.quantile(0.75)
    low_segment = series[series <= low_cutoff]
    high_segment = series[series >= high_cutoff]

    figure, axis = plt.subplots(figsize=(10, 5))
    axis.hist(low_segment, bins=20, alpha=0.6, density=True, label="Low-value segment")
    axis.hist(high_segment, bins=20, alpha=0.6, density=True, label="High-value segment")
    axis.set_title(f"{column_name} Segment Comparison")
    axis.set_xlabel(column_name)
    axis.set_ylabel("Density")
    axis.legend()
    figure.tight_layout()

    output_path = DISTRIBUTION_DIR / f"{column_name.lower()}_segment_comparison.png"
    figure.savefig(output_path, dpi=150)
    plt.close(figure)
    return {
        "column": column_name,
        "low_segment_count": int(low_segment.count()),
        "high_segment_count": int(high_segment.count()),
        "low_cutoff": float(low_cutoff),
        "high_cutoff": float(high_cutoff),
        "plot_file": str(output_path.name),
    }


def analyze_distributions(df):
    numeric_columns = list(df.select_dtypes(include=["number"]).columns)
    report = {
        "summary": {
            "rows": int(len(df)),
            "numeric_columns": numeric_columns,
        },
        "columns": {},
        "segment_comparison": None,
    }

    for column in numeric_columns:
        report["columns"][column] = describe_distribution(df[column])
        save_histogram_and_kde(df[column], column)

    if numeric_columns:
        report["segment_comparison"] = save_segment_comparison(df, numeric_columns[0])

    return report


def main():
    if not PROCESSED_DATA_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {PROCESSED_DATA_FILE}")

    df = load_csv(PROCESSED_DATA_FILE)
    ensure_distribution_dir()

    report = analyze_distributions(df)

    with DISTRIBUTION_REPORT_FILE.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    print("DISTRIBUTION ANALYSIS COMPLETE")
    print(f"Report saved to {DISTRIBUTION_REPORT_FILE}")
    for column, stats_report in report["columns"].items():
        print(f"- {column}: skew={stats_report['skewness']}, kurtosis={stats_report['kurtosis']}")


if __name__ == "__main__":
    main()