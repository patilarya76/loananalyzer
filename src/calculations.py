"""
calculations.py
---------------
Responsible for Feature 4 (Financial Calculations) and Feature 5 (DPD Bucket Classification).

Functions in this module:
1. calculate_outstanding_amount(due_amount, paid_amount)
2. classify_payment_status(due_amount, paid_amount)
3. classify_dpd_bucket(days_past_due)
4. calculate_collection_efficiency(total_collected, total_due)
5. enrich_loan_dataset(df)

All functions include clear boundary condition checks and documented assumptions.
"""

from typing import Union
import pandas as pd
import numpy as np


def calculate_outstanding_amount(due_amount: float, paid_amount: float) -> float:
    """
    Calculates the unpaid balance for an installment.

    Formula:
    --------
    Outstanding Amount = Due Amount - Paid Amount

    Assumptions & Edge Cases:
    --------------------------
    - If paid_amount > due_amount, result is negative (represents overpayment/excess).
    - If due_amount <= 0, returns 0.0 unless flagged.
    """
    if pd.isna(due_amount) or pd.isna(paid_amount):
        return 0.0
    return float(due_amount - paid_amount)


def classify_payment_status(due_amount: float, paid_amount: float) -> str:
    """
    Categorizes loan payment status into:
    - Fully Paid      : Paid amount equals or exceeds due amount.
    - Partially Paid  : Paid amount is greater than 0 but less than due amount.
    - Unpaid          : Paid amount is zero.
    - Under Review    : Negative or irregular amounts.
    """
    if pd.isna(due_amount) or pd.isna(paid_amount) or due_amount <= 0 or paid_amount < 0:
        return "Under Review"

    if paid_amount >= due_amount:
        return "Fully Paid"
    elif 0 < paid_amount < due_amount:
        return "Partially Paid"
    elif paid_amount == 0:
        return "Unpaid"
    else:
        return "Under Review"


def classify_dpd_bucket(dpd: Union[int, float]) -> str:
    """
    Classifies loans into delinquency aging buckets based on Days Past Due (DPD).

    Bucket Definitions (Simplified for practice interview):
    -------------------------------------------------------
    - Current           : 0 DPD
    - Early Delinquency : 1–30 DPD
    - Mid Delinquency   : 31–60 DPD
    - Late Delinquency  : 61–90 DPD
    - 90+ DPD           : > 90 DPD
    - Invalid / Review  : DPD < 0 or NaN

    Disclaimer:
    -----------
    These are simplified project definitions for demonstration purposes and do not
    represent the official classification rules or regulatory NPA definitions of any institution.
    """
    if pd.isna(dpd):
        return "Invalid / Review"

    try:
        val = int(dpd)
    except (ValueError, TypeError):
        return "Invalid / Review"

    if val < 0:
        return "Invalid / Review"
    elif val == 0:
        return "Current"
    elif 1 <= val <= 30:
        return "Early Delinquency (1-30 DPD)"
    elif 31 <= val <= 60:
        return "Mid Delinquency (31-60 DPD)"
    elif 61 <= val <= 90:
        return "Late Delinquency (61-90 DPD)"
    else:  # val > 90
        return "90+ DPD"


def calculate_collection_efficiency(total_collected: float, total_due: float) -> float:
    """
    Calculates collection efficiency percentage at aggregated level.

    Formula:
    --------
    Collection Efficiency (%) = (Total Collected / Total Due) * 100

    Guards:
    -------
    - Prevents ZeroDivisionError when Total Due is 0.
    - Caps efficiency calculation safely to prevent distortion.
    """
    if total_due is None or total_due <= 0:
        return 0.0
    if total_collected is None or total_collected <= 0:
        return 0.0

    efficiency = (total_collected / total_due) * 100.0
    return round(efficiency, 2)


def enrich_loan_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies financial calculations and classifications to each loan in the DataFrame.

    Adds the following computed columns:
    - outstanding_amount : Due Amount - Paid Amount
    - payment_status     : Fully Paid | Partially Paid | Unpaid | Under Review
    - dpd_bucket         : Current | Early Delinquency | Mid Delinquency | Late Delinquency | 90+ DPD
    - overpayment_flag   : Boolean indicating whether paid_amount > due_amount
    """
    enriched = df.copy()

    # Calculate Outstanding Amount
    enriched["outstanding_amount"] = enriched.apply(
        lambda r: calculate_outstanding_amount(r["due_amount"], r["paid_amount"]),
        axis=1
    )

    # Classify Payment Status
    enriched["payment_status"] = enriched.apply(
        lambda r: classify_payment_status(r["due_amount"], r["paid_amount"]),
        axis=1
    )

    # Classify DPD Bucket
    enriched["dpd_bucket"] = enriched["days_past_due"].apply(classify_dpd_bucket)

    # Flag Overpayments
    enriched["overpayment_flag"] = enriched["paid_amount"] > enriched["due_amount"]

    return enriched


if __name__ == "__main__":
    # Test boundary values
    print("Testing DPD bucket boundaries:")
    for test_dpd in [-5, 0, 1, 30, 31, 60, 61, 90, 91, 150]:
        print(f"  DPD {test_dpd:>3} -> {classify_dpd_bucket(test_dpd)}")

    print("\nTesting Efficiency:")
    print(f"  Collected 80k on 100k: {calculate_collection_efficiency(80000, 100000)}%")
    print(f"  Collected 0 on 0:      {calculate_collection_efficiency(0, 0)}%")
