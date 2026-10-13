"""
data_validation.py
------------------
Responsible for Feature 3: Data Cleaning and Validation.

Audits raw loan records against critical business rules:
1. Missing loan IDs (blank, null, NaN).
2. Duplicate loan IDs.
3. Missing or invalid dates (fails datetime parsing).
4. Negative financial figures (loan_amount < 0, due_amount < 0, paid_amount < 0).
5. Overpayments (paid_amount > due_amount) flagged for review.
6. Missing values in important fields (customer_name, branch).
7. Negative Days Past Due (DPD < 0).

CRITICAL POLICY:
Never silently delete suspicious records. Validation issues are cataloged in an
audit log (Data Quality Issues) and segregated from core financial calculations
so portfolio summaries remain mathematically sound and audit-compliant.
"""

from typing import Tuple
import pandas as pd


def validate_loan_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Validates loan records against business integrity rules.

    Parameters:
    -----------
    df : pd.DataFrame
        Raw loan repayment DataFrame.

    Returns:
    --------
    valid_df : pd.DataFrame
        Cleaned records safe for core portfolio financial metrics.
    issues_df : pd.DataFrame
        Audit trail of all detected quality issues, descriptions, and treatments.
    full_audited_df : pd.DataFrame
        The full dataset with 'is_valid' and 'validation_notes' flags appended.
    """
    issues = []
    audited_df = df.copy()

    # Pre-populate tracking columns
    audited_df["is_valid"] = True
    audited_df["validation_flags"] = ""

    # Helper function to log issues
    def log_issue(idx, loan_id, issue_type, severity, description, action):
        issues.append({
            "record_index": idx,
            "loan_id": str(loan_id) if pd.notna(loan_id) and str(loan_id).strip() != "" else "MISSING",
            "issue_type": issue_type,
            "severity": severity,
            "description": description,
            "action_taken": action
        })
        current_flags = audited_df.at[idx, "validation_flags"]
        audited_df.at[idx, "validation_flags"] = f"{current_flags}; {issue_type}".strip("; ")
        if severity == "CRITICAL":
            audited_df.at[idx, "is_valid"] = False

    # -------------------------------------------------------------
    # 1. Check for Missing Loan IDs
    # -------------------------------------------------------------
    missing_id_mask = audited_df["loan_id"].isna() | (audited_df["loan_id"].astype(str).str.strip() == "")
    for idx in audited_df[missing_id_mask].index:
        log_issue(
            idx,
            audited_df.at[idx, "loan_id"],
            "Missing Loan ID",
            "CRITICAL",
            "Loan ID is null or blank. Primary key violation.",
            "Excluded from core financial reporting"
        )

    # -------------------------------------------------------------
    # 2. Check for Duplicate Loan IDs
    # -------------------------------------------------------------
    # Identify non-blank duplicate loan IDs
    non_blank_ids = audited_df.loc[~missing_id_mask, "loan_id"]
    duplicate_mask = non_blank_ids.duplicated(keep=False)
    for idx in non_blank_ids[duplicate_mask].index:
        loan_val = audited_df.at[idx, "loan_id"]
        # Mark subsequent duplicates as critical
        is_subsequent = non_blank_ids.loc[:idx].duplicated().at[idx]
        log_issue(
            idx,
            loan_val,
            "Duplicate Loan ID",
            "CRITICAL" if is_subsequent else "WARNING",
            f"Loan ID '{loan_val}' appears multiple times in the dataset.",
            "Excluded subsequent duplicate from core analysis" if is_subsequent else "Retained primary record"
        )

    # -------------------------------------------------------------
    # 3. Check for Negative Financial Amounts
    # -------------------------------------------------------------
    for idx, row in audited_df.iterrows():
        loan_amt = row.get("loan_amount", 0)
        due_amt = row.get("due_amount", 0)
        paid_amt = row.get("paid_amount", 0)

        if pd.notna(loan_amt) and loan_amt < 0:
            log_issue(
                idx, row.get("loan_id"),
                "Negative Loan Amount", "CRITICAL",
                f"Loan amount is negative ({loan_amt}). Inverted transaction.",
                "Excluded from core financial reporting"
            )
        if pd.notna(due_amt) and due_amt < 0:
            log_issue(
                idx, row.get("loan_id"),
                "Negative Due Amount", "CRITICAL",
                f"Due amount is negative ({due_amt}). Inverted billing.",
                "Excluded from core financial reporting"
            )
        if pd.notna(paid_amt) and paid_amt < 0:
            log_issue(
                idx, row.get("loan_id"),
                "Negative Paid Amount", "CRITICAL",
                f"Paid amount is negative ({paid_amt}). Potential reversal or debit.",
                "Excluded from core financial reporting"
            )

    # -------------------------------------------------------------
    # 4. Check for Overpayments (Paid Amount > Due Amount)
    # -------------------------------------------------------------
    for idx, row in audited_df.iterrows():
        due_amt = row.get("due_amount", 0)
        paid_amt = row.get("paid_amount", 0)
        if pd.notna(due_amt) and pd.notna(paid_amt) and due_amt > 0:
            if paid_amt > due_amt:
                excess = paid_amt - due_amt
                log_issue(
                    idx, row.get("loan_id"),
                    "Payment Exceeds Due", "WARNING",
                    f"Paid amount ({paid_amt}) > Due amount ({due_amt}). Excess: ₹{excess:,.2f}.",
                    "Retained; flagged for suspense ledger audit"
                )

    # -------------------------------------------------------------
    # 5. Check for Missing or Invalid Dates
    # -------------------------------------------------------------
    parsed_due_dates = pd.to_datetime(audited_df["due_date"], errors="coerce")
    for idx in audited_df.index:
        raw_val = audited_df.at[idx, "due_date"]
        if pd.isna(raw_val) or str(raw_val).strip() == "":
            log_issue(
                idx, audited_df.at[idx, "loan_id"],
                "Missing Due Date", "CRITICAL",
                "Due date is empty. Cannot determine aging without billing date.",
                "Excluded from core financial reporting"
            )
        elif pd.isna(parsed_due_dates.at[idx]):
            log_issue(
                idx, audited_df.at[idx, "loan_id"],
                "Invalid Date Format", "CRITICAL",
                f"Due date '{raw_val}' cannot be parsed into standard YYYY-MM-DD format.",
                "Excluded from core financial reporting"
            )

    # -------------------------------------------------------------
    # 6. Check for Negative Days Past Due (DPD < 0)
    # -------------------------------------------------------------
    for idx, row in audited_df.iterrows():
        dpd = row.get("days_past_due")
        if pd.isna(dpd):
            log_issue(
                idx, row.get("loan_id"),
                "Missing DPD", "CRITICAL",
                "Days Past Due is missing / NaN.",
                "Excluded from core financial reporting"
            )
        elif dpd < 0:
            log_issue(
                idx, row.get("loan_id"),
                "Negative DPD", "CRITICAL",
                f"DPD is negative ({dpd}). Indicates advance payment or date anomaly.",
                "Excluded from delinquency classification"
            )

    # -------------------------------------------------------------
    # 7. Check for Missing Customer Name or Branch
    # -------------------------------------------------------------
    for idx, row in audited_df.iterrows():
        cname = str(row.get("customer_name", "")).strip()
        branch = str(row.get("branch", "")).strip()
        if cname == "" or cname.lower() == "nan":
            log_issue(
                idx, row.get("loan_id"),
                "Missing Customer Name", "WARNING",
                "Customer name is missing.",
                "Retained with placeholder 'UNKNOWN CUSTOMER'"
            )
        if branch == "" or branch.lower() == "nan":
            log_issue(
                idx, row.get("loan_id"),
                "Missing Branch", "WARNING",
                "Branch name is missing.",
                "Retained with placeholder 'UNASSIGNED BRANCH'"
            )

    # Construct the issues DataFrame
    if issues:
        issues_df = pd.DataFrame(issues)
    else:
        issues_df = pd.DataFrame(columns=[
            "record_index", "loan_id", "issue_type", "severity", "description", "action_taken"
        ])

    # Subset valid records (where is_valid is True)
    valid_df = audited_df[audited_df["is_valid"]].copy()

    # Fill placeholder values for warnings on valid records
    valid_df["customer_name"] = valid_df["customer_name"].fillna("UNKNOWN CUSTOMER")
    valid_df.loc[valid_df["customer_name"].astype(str).str.strip() == "", "customer_name"] = "UNKNOWN CUSTOMER"
    valid_df["branch"] = valid_df["branch"].fillna("UNASSIGNED BRANCH")
    valid_df.loc[valid_df["branch"].astype(str).str.strip() == "", "branch"] = "UNASSIGNED BRANCH"

    print("\n" + "=" * 70)
    print("  DATA VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total Records Evaluated : {len(audited_df)}")
    print(f"Clean / Valid Records   : {len(valid_df)}")
    print(f"Records with Issues     : {len(issues_df)}")
    critical_count = len(issues_df[issues_df["severity"] == "CRITICAL"]) if not issues_df.empty else 0
    warning_count = len(issues_df[issues_df["severity"] == "WARNING"]) if not issues_df.empty else 0
    print(f"  - Critical Issues (Excluded from Core Portfolio) : {critical_count}")
    print(f"  - Warning Issues  (Retained with Audit Flags)    : {warning_count}")
    print("=" * 70)

    return valid_df, issues_df, audited_df


if __name__ == "__main__":
    from data_loader import load_loan_data
    import os
    sample_file = os.path.join(os.path.dirname(__file__), "..", "data", "loan_data.csv")
    raw = load_loan_data(sample_file)
    v_df, i_df, a_df = validate_loan_data(raw)
    print(i_df[["loan_id", "issue_type", "severity", "action_taken"]].to_string())
