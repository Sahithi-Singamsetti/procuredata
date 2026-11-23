import streamlit as st
import importlib
from pathlib import Path
import pandas as pd
import tempfile

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Project 2 directory
MODULE_DIR = PROJECT_ROOT / "modules" / "02_data_quality"

# Import existing validation module
validate_data = importlib.import_module(
    "modules.02_data_quality.src.validate_data"
)

generate_report = importlib.import_module(
    "modules.02_data_quality.src.generate_report"
)

# Dataset locations
CLEAN_FILE = validate_data.CLEAN_FILE
INPUT_DIR = validate_data.INPUT_DIR

# Page heading
st.title("02 · Data Quality Checker")
st.caption("Project 2 | Purchase Data Validation")

st.divider()

# Dataset Selection
st.subheader("Dataset Selection")

dataset_files = {
    "Clean Dataset": CLEAN_FILE
}

for file_path in sorted(INPUT_DIR.glob("purchases_*.csv")):
    dataset_files[file_path.stem] = file_path

selection_options = list(dataset_files.keys()) + ["Upload a CSV file"]

selected_dataset = st.selectbox(
    "Choose a purchase dataset to validate:",
    options=selection_options
)

uploaded_file = None

if selected_dataset == "Upload a CSV file":

    uploaded_file = st.file_uploader(
        "Upload your purchase dataset",
        type=["csv"]
    )

    if uploaded_file is not None:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv"
        ) as temp_file:

            temp_file.write(uploaded_file.getvalue())
            selected_file = Path(temp_file.name)

        st.success(f"Uploaded: {uploaded_file.name}")

else:

    selected_file = dataset_files[selected_dataset]

    st.success(f"Selected dataset: {selected_file.name}")

# Run Quality Check
st.divider()

st.subheader("Data Quality Analysis")

if st.button(
    "Run Quality Check",
    type="primary",
    disabled=(selected_dataset == "Upload a CSV file" and uploaded_file is None)
):

    try:
        # Load selected dataset
        data = validate_data.load_purchase_file(selected_file)

        # Run validation checks
        issues = validate_data.validate_purchase_file(selected_file)

        # Calculate quality score
        total_records = len(data)
        total_issues = len(issues)

        quality_score = validate_data.calculate_quality_score(
            total_records,
            total_issues
        )

        # Store results
        st.session_state["dq_results"] = {
            "dataset": selected_dataset,
            "total_records": total_records,
            "total_issues": total_issues,
            "quality_score": quality_score,
            "issues": issues
        }

        st.success("Quality check completed successfully!")

    except Exception as e:
        st.error(f"Error during validation: {e}")

# Display validation results
if "dq_results" in st.session_state:

    results = st.session_state["dq_results"]

    if results["dataset"] == selected_dataset:

        st.divider()
        st.subheader("Quality Overview")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Quality Score",
            f'{results["quality_score"]}/100'
        )

        col2.metric(
            "Total Records",
            results["total_records"]
        )

        col3.metric(
            "Issues Detected",
            results["total_issues"]
        )

        st.progress(results["quality_score"] / 100)

        # Issue Analysis
        st.divider()
        st.subheader("Issue Analysis")

        if results["issues"]:

            issues_df = pd.DataFrame(results["issues"])

            st.dataframe(
                issues_df,
                use_container_width=True,
                hide_index=True
            )

        else:
            st.success("No data quality issues found!")

# Excel Report Download
st.divider()

st.subheader("Export Quality Report")

if st.button("Generate Excel Report", type="primary"):

    try:
        generate_report.generate_excel_report()

        report_path = generate_report.REPORT_FILE

        st.session_state["dq_report_bytes"] = report_path.read_bytes()

        st.success("Excel report generated successfully!")

    except Exception as e:
        st.error(f"Error generating report: {e}")

# Download Button
if "dq_report_bytes" in st.session_state:

    st.download_button(
        label="Download Excel Report",
        data=st.session_state["dq_report_bytes"],
        file_name="data_quality_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )