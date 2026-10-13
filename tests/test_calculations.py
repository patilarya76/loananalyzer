"""
test_calculations.py
--------------------
Unit tests for Loan Collection Analyzer using Python's built-in unittest module.

Tests cover:
1. Outstanding Amount Calculation
2. Payment Status Classification
3. DPD Bucket Classification at Boundary Values
4. Collection Efficiency (including ZeroDivisionError prevention)
5. Data Cleaning and Validation Rules (duplicates, negatives, missing values)
6. Excel MIS Report Generation (validating file and required worksheets)
"""

import os
import unittest
import pandas as pd
import openpyxl

from src.calculations import (
    calculate_outstanding_amount,
    classify_payment_status,
    classify_dpd_bucket,
    calculate_collection_efficiency,
    enrich_loan_dataset
)
from src.data_validation import validate_loan_data
from src.report_generator import create_excel_mis_report
from src.analysis import (
    generate_executive_summary_metrics,
    analyze_dpd_buckets,
    analyze_branch_performance,
    analyze_agency_performance
)


class TestLoanCalculations(unittest.TestCase):
    """Test suite for financial formulas and delinquency classification."""

    def test_outstanding_amount_standard(self):
        """Test regular calculation: Due - Paid."""
        self.assertEqual(calculate_outstanding_amount(25000, 10000), 15000.0)
        self.assertEqual(calculate_outstanding_amount(30000, 30000), 0.0)
        self.assertEqual(calculate_outstanding_amount(20000, 0), 20000.0)

    def test_outstanding_amount_overpayment(self):
        """Test overpayment where paid > due produces negative outstanding balance."""
        self.assertEqual(calculate_outstanding_amount(20000, 25000), -5000.0)

    def test_outstanding_amount_missing_values(self):
        """Test handling of NaN or None in amounts."""
        self.assertEqual(calculate_outstanding_amount(None, 10000), 0.0)
        self.assertEqual(calculate_outstanding_amount(20000, None), 0.0)

    def test_payment_status_classification(self):
        """Test payment status categorizations."""
        self.assertEqual(classify_payment_status(25000, 25000), "Fully Paid")
        self.assertEqual(classify_payment_status(25000, 30000), "Fully Paid")  # Overpayment
        self.assertEqual(classify_payment_status(25000, 12000), "Partially Paid")
        self.assertEqual(classify_payment_status(25000, 0), "Unpaid")
        self.assertEqual(classify_payment_status(-5000, 0), "Under Review")

    def test_dpd_bucket_boundaries(self):
        """Test DPD bucket boundaries precisely."""
        # 0 DPD -> Current
        self.assertEqual(classify_dpd_bucket(0), "Current")

        # Early Delinquency: 1 to 30
        self.assertEqual(classify_dpd_bucket(1), "Early Delinquency (1-30 DPD)")
        self.assertEqual(classify_dpd_bucket(15), "Early Delinquency (1-30 DPD)")
        self.assertEqual(classify_dpd_bucket(30), "Early Delinquency (1-30 DPD)")

        # Mid Delinquency: 31 to 60
        self.assertEqual(classify_dpd_bucket(31), "Mid Delinquency (31-60 DPD)")
        self.assertEqual(classify_dpd_bucket(45), "Mid Delinquency (31-60 DPD)")
        self.assertEqual(classify_dpd_bucket(60), "Mid Delinquency (31-60 DPD)")

        # Late Delinquency: 61 to 90
        self.assertEqual(classify_dpd_bucket(61), "Late Delinquency (61-90 DPD)")
        self.assertEqual(classify_dpd_bucket(75), "Late Delinquency (61-90 DPD)")
        self.assertEqual(classify_dpd_bucket(90), "Late Delinquency (61-90 DPD)")

        # 90+ DPD: > 90
        self.assertEqual(classify_dpd_bucket(91), "90+ DPD")
        self.assertEqual(classify_dpd_bucket(180), "90+ DPD")

        # Boundary Edge Cases: Negative and NaN
        self.assertEqual(classify_dpd_bucket(-1), "Invalid / Review")
        self.assertEqual(classify_dpd_bucket(-10), "Invalid / Review")
        self.assertEqual(classify_dpd_bucket(None), "Invalid / Review")
        self.assertEqual(classify_dpd_bucket("corrupt_value"), "Invalid / Review")

    def test_collection_efficiency_calculation(self):
        """Test efficiency percentage calculation and zero-division protection."""
        # Normal 80% recovery
        self.assertEqual(calculate_collection_efficiency(80000, 100000), 80.0)
        # Normal 100% recovery
        self.assertEqual(calculate_collection_efficiency(50000, 50000), 100.0)
        # Zero collected
        self.assertEqual(calculate_collection_efficiency(0, 50000), 0.0)
        # Zero total due (division by zero protection)
        self.assertEqual(calculate_collection_efficiency(0, 0), 0.0)
        self.assertEqual(calculate_collection_efficiency(1000, 0), 0.0)


class TestDataValidation(unittest.TestCase):
    """Test suite for business data validation rules and anomaly detection."""

    def setUp(self):
        # Construct small test DataFrame with deliberate anomalies
        self.sample_df = pd.DataFrame([
            {
                "loan_id": "LN2001",
                "customer_name": "Rohan Deshmukh",
                "branch": "Mumbai - Andheri",
                "collection_agency": "In-House Recovery Team",
                "loan_amount": 1000000,
                "due_amount": 20000,
                "paid_amount": 20000,
                "due_date": "2026-09-05",
                "payment_date": "2026-09-04",
                "days_past_due": 0
            },
            {
                # Missing Loan ID
                "loan_id": "",
                "customer_name": "Test Missing ID",
                "branch": "Pune - Shivaji Nagar",
                "collection_agency": "Apex Recovery Solutions",
                "loan_amount": 1000000,
                "due_amount": 20000,
                "paid_amount": 10000,
                "due_date": "2026-09-05",
                "payment_date": "2026-09-10",
                "days_past_due": 5
            },
            {
                # Duplicate Loan ID
                "loan_id": "LN2001",
                "customer_name": "Duplicate Entry",
                "branch": "Mumbai - Andheri",
                "collection_agency": "In-House Recovery Team",
                "loan_amount": 1000000,
                "due_amount": 20000,
                "paid_amount": 20000,
                "due_date": "2026-09-05",
                "payment_date": "2026-09-04",
                "days_past_due": 0
            },
            {
                # Negative Amount
                "loan_id": "LN2002",
                "customer_name": "Negative Customer",
                "branch": "Delhi - Connaught Place",
                "collection_agency": "Swift Resolution Agents",
                "loan_amount": 1500000,
                "due_amount": -15000,
                "paid_amount": 0,
                "due_date": "2026-09-05",
                "payment_date": "",
                "days_past_due": 45
            },
            {
                # Overpayment (Paid > Due)
                "loan_id": "LN2003",
                "customer_name": "Overpaid Customer",
                "branch": "Jaipur - MI Road",
                "collection_agency": "Pioneer Field Solutions",
                "loan_amount": 1200000,
                "due_amount": 18000,
                "paid_amount": 25000,
                "due_date": "2026-09-05",
                "payment_date": "2026-09-05",
                "days_past_due": 0
            }
        ])

    def test_validation_detects_anomalies(self):
        """Verify that validation flags missing ID, duplicates, negatives, and overpayment."""
        valid_df, issues_df, _ = validate_loan_data(self.sample_df)

        issue_types = issues_df["issue_type"].tolist()
        self.assertIn("Missing Loan ID", issue_types)
        self.assertIn("Duplicate Loan ID", issue_types)
        self.assertIn("Negative Due Amount", issue_types)
        self.assertIn("Payment Exceeds Due", issue_types)

        # Ensure critical issues are excluded from valid_df
        valid_ids = valid_df["loan_id"].dropna().tolist()
        self.assertNotIn("", valid_ids)
        self.assertNotIn("LN2002", valid_ids)


class TestReportGeneration(unittest.TestCase):
    """Test suite verifying automated Excel MIS Report generation."""

    def test_excel_file_and_sheets_created(self):
        """Verify that all 6 worksheets exist in generated Excel file."""
        test_dir = os.path.join(os.path.dirname(__file__), "..", "output")
        test_excel_path = os.path.join(test_dir, "test_mis_report.xlsx")

        # Minimal valid test DataFrame
        df = pd.DataFrame([
            {
                "loan_id": "LN999",
                "customer_name": "Test User",
                "branch": "Mumbai - Andheri",
                "collection_agency": "In-House Recovery Team",
                "loan_amount": 1000000,
                "due_amount": 20000,
                "paid_amount": 15000,
                "due_date": "2026-09-05",
                "payment_date": "2026-09-10",
                "days_past_due": 5
            }
        ])

        valid_df, issues_df, _ = validate_loan_data(df)
        enriched_df = enrich_loan_dataset(valid_df)

        kpis = generate_executive_summary_metrics(enriched_df)
        dpd_summary = analyze_dpd_buckets(enriched_df)
        branch_summary = analyze_branch_performance(enriched_df)
        agency_summary = analyze_agency_performance(enriched_df)

        created_file = create_excel_mis_report(
            test_excel_path,
            executive_kpis=kpis,
            enriched_df=enriched_df,
            dpd_df=dpd_summary,
            branch_df=branch_summary,
            agency_df=agency_summary,
            issues_df=issues_df
        )

        self.assertTrue(os.path.exists(created_file))

        # Inspect workbook sheet names
        wb = openpyxl.load_workbook(created_file)
        expected_sheets = [
            "Executive Summary",
            "Loan Details",
            "DPD Analysis",
            "Branch Performance",
            "Agency Performance",
            "Data Quality Issues"
        ]
        for sheet_name in expected_sheets:
            self.assertIn(sheet_name, wb.sheetnames)

        wb.close()
        # Clean up temporary test file
        if os.path.exists(test_excel_path):
            os.remove(test_excel_path)


if __name__ == "__main__":
    unittest.main()
