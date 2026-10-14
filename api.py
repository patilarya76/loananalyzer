"""
api.py
------
FastAPI Backend Server for Loan Collection Analyzer.

Endpoints:
- GET  /api/health        : Health check
- GET  /api/data          : Complete analysis data (KPIs, buckets, branches, loans, issues)
- POST /api/run-pipeline  : Triggers the data pipeline and regenerates outputs
- GET  /api/download-excel: Downloads the generated collection_mis_report.xlsx
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from src.pipeline_data import get_full_analysis_data, export_frontend_json
from src.main import run_pipeline

app = FastAPI(
    title="LoanPulse Analytics API",
    description="Backend API for LoanPulse Analytics — Automated Loan Collection & Delinquency MIS Dashboard",
    version="1.0.0"
)

# Enable CORS for local Vite development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "Loan Collection Analyzer API"}


@app.get("/api/data")
def get_data():
    try:
        return get_full_analysis_data(PROJECT_ROOT)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/run-pipeline")
def trigger_pipeline():
    try:
        run_pipeline(PROJECT_ROOT)
        export_frontend_json(PROJECT_ROOT)
        return {"status": "success", "message": "Pipeline executed successfully and outputs refreshed."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/download-excel")
def download_excel():
    excel_path = os.path.join(PROJECT_ROOT, "output", "collection_mis_report.xlsx")
    if not os.path.exists(excel_path):
        run_pipeline(PROJECT_ROOT)

    if not os.path.exists(excel_path):
        raise HTTPException(status_code=404, detail="Excel report could not be generated.")

    return FileResponse(
        path=excel_path,
        filename="collection_mis_report.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
