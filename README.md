# Loan Collection Analyzer — Automated MIS Reporting System

> **Practice Mini-Project** designed for technical interview preparation in the Collection Strategy Department at Vastu Housing Finance.  
> *Note: This project utilizes synthetic, fictional loan repayment records to demonstrate Python programming, pandas data analysis, business logic validation, and automated Excel reporting.*

---

## 1. Project Overview & Business Problem

In retail lending and housing finance, loan portfolios require daily and monthly monitoring to minimize credit risk, track recovery agency performance, and identify early signs of default. 

Manual preparation of Management Information System (MIS) reports using fragmented spreadsheets is error-prone, slow, and susceptible to unhandled anomalies (such as negative balances, duplicate entries, or unweighted percentage averages).

The **Loan Collection Analyzer** is a Python-based automated pipeline that:
1. Ingests raw loan repayment data from CSV.
2. Audits data quality and isolates anomalies without silent record deletion.
3. Calculates standard delinquency metrics (Days Past Due, Outstanding Amount, Collection Efficiency).
4. Classifies loans into delinquency aging buckets.
5. Aggregates performance across branches and collection agencies.
6. Generates visual charts and an executive-ready, multi-sheet Excel MIS report (`output/collection_mis_report.xlsx`).

---

## 2. Technology Stack

- **Python 3.10+**: Core programming language.
- **pandas**: Tabular data manipulation, grouping, aggregations, and filtering.
- **NumPy**: Numeric operations and array handling.
- **openpyxl**: Automated Excel report creation, styling, cell formatting, and embedded charts.
- **Matplotlib**: Portfolio visual analytics and bar charts.
- **unittest**: Built-in automated unit testing framework.

---

## 3. Project Structure

```text
loananalyzer/
├── data/
│   └── loan_data.csv                 # 115 synthetic loan records including deliberate edge cases
├── output/
│   └── collection_mis_report.xlsx     # Generated 6-sheet formatted Excel MIS report
├── charts/
│   ├── dpd_outstanding_amount.png     # Visual chart: Outstanding balance by DPD bucket
│   └── branch_collection_efficiency.png # Visual chart: Collection efficiency by branch
├── src/
│   ├── __init__.py                   # Package initializer
│   ├── data_loader.py                # Ingestion and basic structural validation
│   ├── data_validation.py            # Business validation rules and audit logging
│   ├── calculations.py               # Financial formulas and DPD bucketing logic
│   ├── analysis.py                   # Aggregation by DPD, Branch, Agency, and Status
│   ├── report_generator.py           # openpyxl multi-sheet Excel generator
│   └── main.py                       # Pipeline orchestrator and console dashboard
├── tests/
│   └── test_calculations.py          # 8 automated unit tests covering calculations & logic
├── generate_dataset.py               # Deterministic dataset generation script
├── requirements.txt                  # Python dependencies
├── README.md                         # Documentation and interview guide
└── .gitignore                        # Git exclusion rules
```

---

## 4. Key Business Metrics & Formulas

| Metric | Formula | Business Purpose |
| :--- | :--- | :--- |
| **Outstanding Amount** | $\text{Due Amount} - \text{Paid Amount}$ | Identifies unpaid installment balance. Negative values flag overpayment. |
| **Collection Efficiency (%)** | $\left( \frac{\sum \text{Paid Amount}}{\sum \text{Due Amount}} \right) \times 100$ | Measures overall recovery effectiveness. Calculated on aggregated sums to avoid distortion. |
| **Days Past Due (DPD)** | Count of days elapsed past the contractual due date | Primary metric for assessing delinquency aging. |
| **Share of Outstanding (%)** | $\left( \frac{\text{Bucket Outstanding}}{\text{Total Portfolio Outstanding}} \right) \times 100$ | Identifies portfolio concentration of delinquent capital. |

### DPD Aging Bucket Classification
- **Current**: $0 \text{ DPD}$ (Up to date)
- **Early Delinquency**: $1 \text{ to } 30 \text{ DPD}$ (Soft bucket, early reminder stage)
- **Mid Delinquency**: $31 \text{ to } 60 \text{ DPD}$ (Medium risk, escalated collection)
- **Late Delinquency**: $61 \text{ to } 90 \text{ DPD}$ (High risk, intensive recovery)
- **90+ DPD**: $> 90 \text{ DPD}$ (Hard delinquency / Default review)
- **Invalid / Review**: $\text{DPD} < 0$ or unparseable values

*(Disclaimer: These are simplified project definitions for demonstration purposes and do not represent the official regulatory NPA definitions of any financial institution.)*

---

## 5. Data Quality Assumptions & Edge Case Handling

Instead of silently deleting bad data, the validation engine (`src/data_validation.py`) enforces strict audit standards:
1. **Missing or Blank Loan IDs**: Treated as `CRITICAL` primary key violations and excluded from portfolio metrics.
2. **Duplicate Loan IDs**: The first instance is retained; subsequent duplicate entries are marked `CRITICAL` and segregated.
3. **Negative Financial Figures**: Negative loan, due, or paid amounts are flagged as `CRITICAL` inverted transactions.
4. **Overpayment (Paid > Due)**: Flagged as `WARNING`. The loan is retained in the dataset, but flagged for suspense ledger audit.
5. **Corrupted or Missing Dates**: Marked as `CRITICAL` and excluded from aging analysis.
6. **Negative DPD**: Flagged as `CRITICAL` date anomalies and routed for manual review.
7. **Audit Log**: All flagged records are exported to the `Data Quality Issues` worksheet in the Excel report with root-cause explanations and corrective actions.

---

## 6. Installation & Execution Guide

### Prerequisites
- Python 3.10 or higher installed on Windows.

### Windows PowerShell Commands

1. **Clone or Navigate to the Project Root**:
   ```powershell
   cd c:\Users\lenovo\Desktop\loananalyzer
   ```

2. **Create and Activate a Virtual Environment** (Optional but Recommended):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install Dependencies**:
   ```powershell
   python -m pip install -r requirements.txt
   ```

4. **Run the Automated MIS Pipeline**:
   ```powershell
   python -m src.main
   ```

5. **Run the Automated Unit Tests**:
   ```powershell
   python -m unittest tests/test_calculations.py
   ```

6. **Locate and Open the Excel MIS Report**:
   ```powershell
   Invoke-Item .\output\collection_mis_report.xlsx
   ```

---

## 7. Generated Excel Report Structure

The generated workbook (`output/collection_mis_report.xlsx`) contains 6 styled worksheets:

1. **`Executive Summary`**: High-level KPI cards (Total Loans, Total Due, Total Collected, Total Outstanding, Collection Efficiency %) and portfolio summary.
2. **`Loan Details`**: Full row-level ledger with formatted currency, payment statuses, and frozen header rows.
3. **`DPD Analysis`**: Delinquency aging table with an embedded openpyxl column chart showing outstanding amount distribution.
4. **`Branch Performance`**: Branch scorecard ranked by collection efficiency.
5. **`Agency Performance`**: Performance ranking for internal and third-party recovery teams.
6. **`Data Quality Issues`**: Complete audit log of all records flagged during data validation.

---

## 8. Limitations and Future Improvements

- **Database Connectivity**: Currently reads static CSV files; could be extended to query SQL databases (PostgreSQL, MySQL, SQL Server) directly.
- **Roll Rate Matrix**: Could implement a transition matrix tracking loans moving between delinquency buckets month-over-month.
- **Automated Email Dispatch**: Could integrate Python `smtplib` to automatically email the Excel MIS report to branch managers daily.
- **Power BI / BI Tool Integration**: Clean aggregated tables can be scheduled as automated data sources for enterprise Power BI dashboards.
