from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
PROCESSED_DATA_FILE = BASE_DIR / "output" / "processed_cloud_data.csv"
RAW_DATA_FILE = BASE_DIR / "data" / "raw" / "cloud_data.csv"


@st.cache_data(show_spinner=False)
def load_data():
	data_file = PROCESSED_DATA_FILE if PROCESSED_DATA_FILE.exists() else RAW_DATA_FILE
	if not data_file.exists():
		raise FileNotFoundError(f"No dataset found at {PROCESSED_DATA_FILE} or {RAW_DATA_FILE}")
	return pd.read_csv(data_file), data_file


def percent_change(current_value, baseline_value):
	if baseline_value in (None, 0) or pd.isna(baseline_value) or pd.isna(current_value):
		return None
	return ((current_value - baseline_value) / baseline_value) * 100


def format_value(value, kind):
	if value is None or pd.isna(value):
		return "N/A"
	if kind == "count":
		return f"{int(round(value)):,}"
	if kind == "currency":
		return f"${value:,.0f}"
	if kind == "percent":
		return f"{value:,.1f}%"
	return f"{value:,.2f}"


def render_kpi_cards(filtered, baseline):
	metrics = [
		{
			"label": "Rows",
			"kind": "count",
			"current": len(filtered),
			"baseline": len(baseline),
			"delta_color": "normal",
		},
		{
			"label": "Avg Infrastructure Cost",
			"kind": "currency",
			"current": filtered["InfrastructureCost"].mean() if "InfrastructureCost" in filtered.columns else None,
			"baseline": baseline["InfrastructureCost"].mean() if "InfrastructureCost" in baseline.columns else None,
			"delta_color": "inverse",
		},
		{
			"label": "Avg CPU Usage",
			"kind": "percent",
			"current": filtered["CPUUsage"].mean() if "CPUUsage" in filtered.columns else None,
			"baseline": baseline["CPUUsage"].mean() if "CPUUsage" in baseline.columns else None,
			"delta_color": "normal",
		},
		{
			"label": "Projects Covered",
			"kind": "count",
			"current": filtered["ProjectID"].nunique(dropna=True) if "ProjectID" in filtered.columns else None,
			"baseline": baseline["ProjectID"].nunique(dropna=True) if "ProjectID" in baseline.columns else None,
			"delta_color": "normal",
		},
		{
			"label": "Services Covered",
			"kind": "count",
			"current": filtered["CloudService"].nunique(dropna=True) if "CloudService" in filtered.columns else None,
			"baseline": baseline["CloudService"].nunique(dropna=True) if "CloudService" in baseline.columns else None,
			"delta_color": "normal",
		},
	]

	columns = st.columns(len(metrics))
	for column, metric in zip(columns, metrics):
		current_value = format_value(metric["current"], metric["kind"])
		delta_pct = percent_change(metric["current"], metric["baseline"])
		delta_text = None if delta_pct is None else f"{delta_pct:+.1f}%"
		with column:
			st.metric(metric["label"], current_value, delta=delta_text, delta_color=metric["delta_color"])


def main():
	st.set_page_config(page_title="InfraVision Dashboard", layout="wide")
	st.title("InfraVision Interactive Dashboard")
	st.caption("Interactive Plotly charts for cloud infrastructure billing data.")

	df, data_file = load_data()
	baseline = df.copy()

	st.sidebar.header("Filters")
	services = sorted(df["CloudService"].dropna().unique()) if "CloudService" in df.columns else []
	selected_services = st.sidebar.multiselect("Cloud service", services, default=services)

	projects = sorted(df["ProjectID"].dropna().unique()) if "ProjectID" in df.columns else []
	selected_projects = st.sidebar.multiselect("Project", projects, default=projects)

	filtered = df.copy()
	if selected_services and "CloudService" in filtered.columns:
		filtered = filtered[filtered["CloudService"].isin(selected_services)]
	if selected_projects and "ProjectID" in filtered.columns:
		filtered = filtered[filtered["ProjectID"].isin(selected_projects)]

	metric_columns = [column for column in ["InfrastructureCost", "CPUUsage"] if column in filtered.columns]
	metric = st.sidebar.selectbox("Metric", metric_columns) if metric_columns else None
	group_options = [column for column in ["ProjectID", "CloudService", "BillingID"] if column in filtered.columns]
	group_by = st.sidebar.selectbox("Group by", group_options) if group_options else None

	render_kpi_cards(filtered, baseline)
	st.caption("KPI deltas compare the filtered view to the full dataset because the source data does not include a time column for period-over-period comparisons.")
	st.divider()

	if filtered.empty or metric is None or group_by is None:
		st.warning("No rows match the selected filters or required columns are missing.")
		return

	agg = filtered.groupby(group_by, dropna=False)[metric].mean().reset_index()
	bar_chart = px.bar(
		agg,
		x=group_by,
		y=metric,
		color=group_by,
		title=f"Average {metric} by {group_by}",
	)
	bar_chart.update_traces(hovertemplate=f"{group_by}: %{{x}}<br>{metric}: %{{y:,.2f}}<extra></extra>")
	bar_chart.update_layout(showlegend=False, height=520)
	st.plotly_chart(bar_chart, use_container_width=True)

	left, right = st.columns(2)

	with left:
		scatter_x = "CPUUsage" if "CPUUsage" in filtered.columns else filtered.columns[0]
		scatter_y = "InfrastructureCost" if "InfrastructureCost" in filtered.columns else filtered.columns[0]
		scatter = px.scatter(
			filtered,
			x=scatter_x,
			y=scatter_y,
			color="CloudService" if "CloudService" in filtered.columns else None,
			hover_data=[column for column in ["BillingID", "ProjectID"] if column in filtered.columns],
			title="Infrastructure Cost vs CPU Usage",
		)
		scatter.update_traces(marker=dict(size=12, opacity=0.8))
		st.plotly_chart(scatter, use_container_width=True)

	with right:
		st.subheader("Filtered data preview")
		st.dataframe(filtered.head(10), use_container_width=True)

	st.download_button(
		label="Download filtered data as CSV",
		data=filtered.to_csv(index=False).encode("utf-8"),
		file_name="infra_vision_filtered_data.csv",
		mime="text/csv",
	)


if __name__ == "__main__":
	main()