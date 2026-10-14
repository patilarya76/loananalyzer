"""
pipeline_data.py
----------------
Provides data transformation and serialization for the React Frontend
and the FastAPI backend.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any
import numpy as np

from src.data_loader import load_loan_data
from src.data_validation import validate_loan_data
from src.calculations import enrich_loan_dataset
from src.analysis import (
    generate_executive_summary_metrics,
    analyze_dpd_buckets,
    analyze_branch_performance,
    analyze_agency_performance,
    analyze_payment_status,
)


class CustomJSONEncoder(json.JSONEncoder):
    """Encodes numpy and pandas specific data types into native Python JSON types."""
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        return super().default(obj)


def get_full_analysis_data(project_root: str = None) -> Dict[str, Any]:
    """
    Executes the analysis pipeline in memory and returns a clean, serializable
    dictionary structure for web and API consumption.
    """
    if project_root is None:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    data_file = os.path.join(project_root, "data", "loan_data.csv")
    raw_df = load_loan_data(data_file)
    valid_df, issues_df, audited_df = validate_loan_data(raw_df)
    enriched_df = enrich_loan_dataset(valid_df)

    # Performance analysis summaries
    kpis = generate_executive_summary_metrics(enriched_df)
    dpd_df = analyze_dpd_buckets(enriched_df)
    branch_df = analyze_branch_performance(enriched_df)
    agency_df = analyze_agency_performance(enriched_df)
    payment_status_df = analyze_payment_status(enriched_df)

    # Use to_json to cleanly convert pandas DataFrames to JSON-safe python objects
    loans_list = json.loads(enriched_df.fillna("").to_json(orient="records"))
    issues_list = json.loads(issues_df.fillna("").to_json(orient="records"))
    dpd_list = json.loads(dpd_df.fillna(0).to_json(orient="records"))
    branch_list = json.loads(branch_df.fillna(0).to_json(orient="records"))
    agency_list = json.loads(agency_df.fillna(0).to_json(orient="records"))
    payment_status_list = json.loads(payment_status_df.fillna(0).to_json(orient="records"))

    # Convert KPI numbers to native types
    safe_kpis = {}
    for k, v in kpis.items():
        if isinstance(v, (np.integer, np.int64, np.int32)):
            safe_kpis[k] = int(v)
        elif isinstance(v, (np.floating, np.float64, np.float32)):
            safe_kpis[k] = float(v)
        else:
            safe_kpis[k] = v

    # Distinct filter options
    branches = sorted(list(set(enriched_df["branch"].dropna().unique())))
    agencies = sorted(list(set(enriched_df["collection_agency"].dropna().unique())))
    dpd_buckets = [
        "Current",
        "Early Delinquency (1-30 DPD)",
        "Mid Delinquency (31-60 DPD)",
        "Late Delinquency (61-90 DPD)",
        "90+ DPD"
    ]
    payment_statuses = ["Fully Paid", "Partially Paid", "Unpaid", "Under Review"]

    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "kpis": safe_kpis,
        "dpd_buckets": dpd_list,
        "branch_performance": branch_list,
        "agency_performance": agency_list,
        "payment_status": payment_status_list,
        "loans": loans_list,
        "issues": issues_list,
        "filters": {
            "branches": branches,
            "agencies": agencies,
            "dpd_buckets": dpd_buckets,
            "payment_statuses": payment_statuses
        }
    }


def export_frontend_json(project_root: str = None) -> str:
    """
    Exports the complete analysis data to frontend/public/data.json
    so that the React frontend can function instantly offline or via static hosting.
    """
    if project_root is None:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    data = get_full_analysis_data(project_root)
    output_path = os.path.join(project_root, "frontend", "public", "data.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, cls=CustomJSONEncoder)

    print(f"Exported frontend data JSON to: {output_path}")
    return output_path


if __name__ == "__main__":
    export_frontend_json()
