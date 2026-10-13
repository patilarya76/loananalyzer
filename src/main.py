"""
main.py
-------
Main execution script for Loan Collection Analyzer — Automated MIS Reporting System.

Workflow:
1. Ingest loan data from CSV.
2. Validate records and generate an audit log of issues.
3. Compute financial calculations (Outstanding Amount, Payment Status, DPD Buckets).
4. Perform collection performance analysis across DPD, branches, and agencies.
5. Generate visual analytics charts with Matplotlib in 'charts/'.
6. Produce formatted multi-sheet Excel MIS report in 'output/'.
7. Display high-level executive summary on console.
"""

import os
import sys

# Configure UTF-8 for console output on Windows to prevent charmap encoding errors
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import matplotlib
# Use non-interactive backend for headless / script execution
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from src.data_loader import load_loan_data
from src.data_validation import validate_loan_data
from src.calculations import enrich_loan_dataset
from src.analysis import (
    generate_executive_summary_metrics,
    analyze_dpd_buckets,
    analyze_branch_performance,
    analyze_agency_performance,
    analyze_payment_status,
    get_top_performing_branches,
    get_top_performing_agencies,
)
from src.report_generator import create_excel_mis_report


def generate_visual_charts(dpd_df: pd.DataFrame, branch_df: pd.DataFrame, charts_dir: str):
    """
    Generates clean Matplotlib charts and saves them to the charts/ directory.
    """
    os.makedirs(charts_dir, exist_ok=True)

    # 1. Bar Chart: Outstanding Amount by DPD Bucket
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(
        dpd_df["dpd_bucket"],
        dpd_df["total_outstanding"] / 100000.0,  # In Lakhs for readability
        color="#1F4E79",
        edgecolor="#0D233A",
        width=0.55
    )
    ax.set_title("Total Outstanding Amount by DPD Bucket (in Lakhs ₹)", fontsize=13, fontweight="bold", pad=15)
    ax.set_ylabel("Outstanding Balance (₹ Lakhs)", fontsize=10)
    ax.set_xlabel("Delinquency Aging Bucket", fontsize=10)
    plt.xticks(rotation=20, ha="right", fontsize=9)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    # Value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.annotate(f"₹{height:.1f}L",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 4), textcoords="offset points",
                        ha="center", va="bottom", fontsize=8, fontweight="bold")

    plt.tight_layout()
    chart1_path = os.path.join(charts_dir, "dpd_outstanding_amount.png")
    plt.savefig(chart1_path, dpi=200)
    plt.close()

    # 2. Bar Chart: Collection Efficiency by Branch
    fig, ax = plt.subplots(figsize=(10, 5))
    branch_sorted = branch_df.sort_values("collection_efficiency_pct", ascending=True)
    bars = ax.barh(
        branch_sorted["branch"],
        branch_sorted["collection_efficiency_pct"],
        color="#2E75B6",
        edgecolor="#1F4E79",
        height=0.55
    )
    ax.set_title("Collection Efficiency by Branch (%)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Collection Efficiency (%)", fontsize=10)
    ax.set_xlim(0, 105)
    ax.axvline(80, color="#C00000", linestyle=":", label="80% Target Benchmark")
    ax.grid(axis="x", linestyle="--", alpha=0.5)
    ax.legend(loc="lower right")

    for bar in bars:
        width = bar.get_width()
        ax.annotate(f"{width:.1f}%",
                    xy=(width, bar.get_y() + bar.get_height() / 2),
                    xytext=(5, 0), textcoords="offset points",
                    ha="left", va="center", fontsize=8, fontweight="bold")

    plt.tight_layout()
    chart2_path = os.path.join(charts_dir, "branch_collection_efficiency.png")
    plt.savefig(chart2_path, dpi=200)
    plt.close()

    return chart1_path, chart2_path


def run_pipeline(project_root: str = None):
    """
    Executes the end-to-end Loan Collection Analyzer workflow.
    """
    if project_root is None:
        # Defaults to parent directory of src/
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    data_file = os.path.join(project_root, "data", "loan_data.csv")
    output_report = os.path.join(project_root, "output", "collection_mis_report.xlsx")
    charts_dir = os.path.join(project_root, "charts")

    print("\n" + "=" * 75)
    print("  LOAN COLLECTION ANALYZER — AUTOMATED MIS REPORTING SYSTEM")
    print("  Vastu Housing Finance | Collection Strategy Department")
    print("=" * 75)

    # Step 1: Data Ingestion
    print("\n[Step 1/6] Ingesting loan data...")
    raw_df = load_loan_data(data_file)

    # Step 2: Data Cleaning and Validation
    print("\n[Step 2/6] Validating business rules & detecting anomalies...")
    valid_df, issues_df, audited_df = validate_loan_data(raw_df)

    # Step 3: Financial Calculations & DPD Classification
    print("\n[Step 3/6] Applying financial formulas and DPD bucketing...")
    enriched_df = enrich_loan_dataset(valid_df)

    # Step 4: Collection Performance Analytics
    print("\n[Step 4/6] Aggregating portfolio, DPD, branch & agency metrics...")
    executive_kpis = generate_executive_summary_metrics(enriched_df)
    dpd_summary = analyze_dpd_buckets(enriched_df)
    branch_summary = analyze_branch_performance(enriched_df)
    agency_summary = analyze_agency_performance(enriched_df)
    payment_status_summary = analyze_payment_status(enriched_df)
    top_branches = get_top_performing_branches(branch_summary, top_n=5)
    top_agencies = get_top_performing_agencies(agency_summary, top_n=5)

    # Step 5: Visual Chart Generation
    print("\n[Step 5/6] Generating analytical visual charts...")
    chart1, chart2 = generate_visual_charts(dpd_summary, branch_summary, charts_dir)
    print(f"  - Chart saved: {os.path.relpath(chart1, project_root)}")
    print(f"  - Chart saved: {os.path.relpath(chart2, project_root)}")

    # Step 6: Automated Excel MIS Report Generation
    print("\n[Step 6/6] Generating formatted Excel MIS Report with openpyxl...")
    report_file = create_excel_mis_report(
        output_report,
        executive_kpis=executive_kpis,
        enriched_df=enriched_df,
        dpd_df=dpd_summary,
        branch_df=branch_summary,
        agency_df=agency_summary,
        issues_df=issues_df
    )
    print(f"  - Report generated successfully: {os.path.relpath(report_file, project_root)}")

    # -------------------------------------------------------------
    # Executive Console Summary
    # -------------------------------------------------------------
    print("\n" + "=" * 75)
    print("  EXECUTIVE PORTFOLIO DASHBOARD")
    print("=" * 75)
    print(f"  Total Valid Loans Analyzed : {executive_kpis['Total Active Loans']}")
    print(f"  Total Due Billing Amount   : INR {executive_kpis['Total Billing Due Amount']:,.2f}")
    print(f"  Total Amount Collected     : INR {executive_kpis['Total Amount Collected']:,.2f}")
    print(f"  Total Outstanding Balance  : INR {executive_kpis['Total Outstanding Amount']:,.2f}")
    print(f"  Overall Collection Rate    : {executive_kpis['Overall Collection Efficiency (%)']:.2f}%")
    print(f"  Data Quality Flags Logged  : {len(issues_df)} (Audited in 'Data Quality Issues')")
    print("-" * 75)

    print("\n[DPD Aging Bucket Distribution]")
    print(dpd_summary[["dpd_bucket", "loan_count", "total_outstanding", "collection_efficiency_pct"]].to_string(index=False))

    print("\n[Top 5 Branches by Collection Efficiency]")
    print(top_branches[["branch", "loan_count", "collection_efficiency_pct"]].to_string(index=False))

    print("\n[Payment Status Distribution]")
    print(payment_status_summary[["payment_status", "loan_count", "share_of_loans_pct"]].to_string(index=False))

    print("\n" + "=" * 75)
    print("  PIPELINE EXECUTION COMPLETE")
    print(f"  Excel MIS Report : {report_file}")
    print(f"  Charts Location  : {charts_dir}")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    run_pipeline()
