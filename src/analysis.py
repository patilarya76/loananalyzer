"""
analysis.py
-----------
Responsible for Feature 6: Collection Performance Analysis.

Generates aggregated reporting summaries:
1. Executive Summary KPIs
2. DPD Bucket Analysis
3. Branch Performance Analysis
4. Collection Agency Performance Analysis
5. Payment Status Distribution
6. Top 5 Rankings (with loan counts for statistical context)

INTERVIEW BEST PRACTICE:
Always calculate Collection Efficiency using aggregated totals:
(Sum of Collected / Sum of Due) * 100.
Never compute the arithmetic mean of individual loan percentages, which causes
unweighted distortion.
"""

from typing import Dict, Any
import pandas as pd


def generate_executive_summary_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Computes portfolio-level key performance indicators (KPIs).
    """
    total_loans = len(df)
    total_portfolio = df["loan_amount"].sum()
    total_due = df["due_amount"].sum()
    total_collected = df["paid_amount"].sum()
    total_outstanding = df["outstanding_amount"].sum()

    overall_efficiency = (
        (total_collected / total_due * 100.0) if total_due > 0 else 0.0
    )

    overpaid_count = int(df["overpayment_flag"].sum()) if "overpayment_flag" in df.columns else 0

    return {
        "Total Active Loans": total_loans,
        "Total Loan Portfolio (Principal)": round(total_portfolio, 2),
        "Total Billing Due Amount": round(total_due, 2),
        "Total Amount Collected": round(total_collected, 2),
        "Total Outstanding Amount": round(total_outstanding, 2),
        "Overall Collection Efficiency (%)": round(overall_efficiency, 2),
        "Loans with Overpayment Flag": overpaid_count,
    }


def analyze_dpd_buckets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarizes loan aging across DPD buckets.
    """
    grouped = df.groupby("dpd_bucket", observed=False).agg(
        loan_count=("loan_id", "count"),
        total_due=("due_amount", "sum"),
        total_collected=("paid_amount", "sum"),
        total_outstanding=("outstanding_amount", "sum")
    ).reset_index()

    # Calculate collection efficiency using aggregated totals
    grouped["collection_efficiency_pct"] = grouped.apply(
        lambda r: round((r["total_collected"] / r["total_due"] * 100.0), 2) if r["total_due"] > 0 else 0.0,
        axis=1
    )

    # Share of portfolio outstanding
    tot_out = grouped["total_outstanding"].sum()
    grouped["share_of_outstanding_pct"] = grouped["total_outstanding"].apply(
        lambda x: round((x / tot_out * 100.0), 2) if tot_out > 0 else 0.0
    )

    # Define logical ordering for delinquency presentation
    bucket_order = [
        "Current",
        "Early Delinquency (1-30 DPD)",
        "Mid Delinquency (31-60 DPD)",
        "Late Delinquency (61-90 DPD)",
        "90+ DPD",
        "Invalid / Review"
    ]
    grouped["sort_key"] = grouped["dpd_bucket"].map(
        lambda b: bucket_order.index(b) if b in bucket_order else 99
    )
    grouped = grouped.sort_values("sort_key").drop(columns=["sort_key"]).reset_index(drop=True)

    return grouped


def analyze_branch_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarizes collection metrics aggregated by branch.
    """
    grouped = df.groupby("branch", observed=False).agg(
        loan_count=("loan_id", "count"),
        total_due=("due_amount", "sum"),
        total_collected=("paid_amount", "sum"),
        total_outstanding=("outstanding_amount", "sum")
    ).reset_index()

    grouped["collection_efficiency_pct"] = grouped.apply(
        lambda r: round((r["total_collected"] / r["total_due"] * 100.0), 2) if r["total_due"] > 0 else 0.0,
        axis=1
    )

    # Sort descending by collection efficiency
    grouped = grouped.sort_values(by="collection_efficiency_pct", ascending=False).reset_index(drop=True)
    return grouped


def analyze_agency_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarizes recovery metrics aggregated by collection agency.
    """
    grouped = df.groupby("collection_agency", observed=False).agg(
        loan_count=("loan_id", "count"),
        total_due=("due_amount", "sum"),
        total_collected=("paid_amount", "sum"),
        total_outstanding=("outstanding_amount", "sum")
    ).reset_index()

    grouped["collection_efficiency_pct"] = grouped.apply(
        lambda r: round((r["total_collected"] / r["total_due"] * 100.0), 2) if r["total_due"] > 0 else 0.0,
        axis=1
    )

    # Sort descending by collection efficiency
    grouped = grouped.sort_values(by="collection_efficiency_pct", ascending=False).reset_index(drop=True)
    return grouped


def analyze_payment_status(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarizes portfolio breakdown by payment status.
    """
    grouped = df.groupby("payment_status", observed=False).agg(
        loan_count=("loan_id", "count"),
        total_due=("due_amount", "sum"),
        total_collected=("paid_amount", "sum"),
        total_outstanding=("outstanding_amount", "sum")
    ).reset_index()

    total_loans = len(df)
    grouped["share_of_loans_pct"] = grouped["loan_count"].apply(
        lambda c: round((c / total_loans * 100.0), 2) if total_loans > 0 else 0.0
    )

    return grouped


def get_top_performing_branches(branch_df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Returns the top N branches by collection efficiency.
    Always displays loan_count to provide sample size context.
    """
    return branch_df.head(top_n).copy()


def get_top_performing_agencies(agency_df: pd.DataFrame, top_n: int = 5) -> pd.DataFrame:
    """
    Returns the top N collection agencies by collection efficiency.
    Always displays loan_count to provide sample size context.
    """
    return agency_df.head(top_n).copy()


if __name__ == "__main__":
    from data_loader import load_loan_data
    from data_validation import validate_loan_data
    from calculations import enrich_loan_dataset
    import os

    sample_file = os.path.join(os.path.dirname(__file__), "..", "data", "loan_data.csv")
    raw = load_loan_data(sample_file)
    valid, _, _ = validate_loan_data(raw)
    enriched = enrich_loan_dataset(valid)

    kpis = generate_executive_summary_metrics(enriched)
    print("\nExecutive KPIs:")
    for k, v in kpis.items():
        print(f"  {k:<35}: {v}")

    print("\nDPD Summary:")
    print(analyze_dpd_buckets(enriched).to_string(index=False))
