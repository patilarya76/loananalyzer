import React, { useState, useEffect } from 'react';
import { 
  BarChart3, 
  Building2, 
  ShieldCheck, 
  FileText, 
  AlertTriangle, 
  LayoutDashboard, 
  Download, 
  RefreshCw, 
  Landmark,
  CheckCircle2,
  Clock,
  Sparkles
} from 'lucide-react';

import KPICards from './components/KPICards';
import DPDChart from './components/DPDChart';
import BranchChart from './components/BranchChart';
import LoanTable from './components/LoanTable';
import IssuesTable from './components/IssuesTable';
import { BranchTable, AgencyTable, DPDTable } from './components/ScorecardTables';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isLiveApi, setIsLiveApi] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState('');

  const API_BASE = 'http://127.0.0.1:8000';

  // Load analysis data
  const fetchData = async () => {
    setLoading(true);
    try {
      // 1. Attempt connection to FastAPI live backend
      const res = await fetch(`${API_BASE}/api/data`, { signal: AbortSignal.timeout(2000) });
      if (res.ok) {
        const json = await res.json();
        setData(json);
        setIsLiveApi(true);
        setLoading(false);
        return;
      }
    } catch (err) {
      // API not available, proceed to static fallback
    }

    // 2. Fallback to pre-exported static data.json
    try {
      const staticRes = await fetch('/data.json');
      if (staticRes.ok) {
        const json = await staticRes.json();
        setData(json);
        setIsLiveApi(false);
      } else {
        throw new Error('Failed to load static data.json');
      }
    } catch (err) {
      console.error('Error loading data:', err);
      setFeedbackMessage('Failed to load dataset. Please ensure backend or data.json is available.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Trigger pipeline re-run on backend
  const handleRunPipeline = async () => {
    setIsRefreshing(true);
    setFeedbackMessage('');
    try {
      if (isLiveApi) {
        const res = await fetch(`${API_BASE}/api/run-pipeline`, { method: 'POST' });
        if (res.ok) {
          await fetchData();
          showTemporaryMessage('Pipeline re-executed and dashboard updated!');
        } else {
          showTemporaryMessage('Backend returned error during execution.');
        }
      } else {
        // When in static mode
        showTemporaryMessage('Running in Static Mode. To trigger live execution, start "python api.py".');
      }
    } catch (err) {
      showTemporaryMessage('Could not reach backend API.');
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleDownloadExcel = () => {
    if (isLiveApi) {
      window.location.href = `${API_BASE}/api/download-excel`;
    } else {
      showTemporaryMessage('Excel report is saved in "output/collection_mis_report.xlsx" in your project folder.');
    }
  };

  const showTemporaryMessage = (msg) => {
    setFeedbackMessage(msg);
    setTimeout(() => {
      setFeedbackMessage('');
    }, 4500);
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh', gap: '1rem' }}>
        <RefreshCw size={36} className="spin" style={{ color: '#2563eb' }} />
        <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#0f172a' }}>Loading Loan Collection MIS Analytics...</h2>
        <p style={{ color: '#64748b', fontSize: '0.9rem' }}>Ingesting repayment data and computing delinquency metrics</p>
      </div>
    );
  }

  const kpis = data?.kpis;
  const dpdBuckets = data?.dpd_buckets || [];
  const branchPerformance = data?.branch_performance || [];
  const agencyPerformance = data?.agency_performance || [];
  const loans = data?.loans || [];
  const issues = data?.issues || [];
  const filters = data?.filters || {};

  return (
    <div className="app-container">
      {/* Top Header */}
      <header className="top-header">
        <div className="header-content">
          <div className="brand-section">
            <div className="brand-logo-icon">
              <Landmark size={24} />
            </div>
            <div className="brand-titles">
              <h1>
                LOANPULSE ANALYTICS
                <span className="brand-badge">Collection MIS</span>
              </h1>
              <p className="brand-subtitle">Automated Loan Delinquency & Recovery Analytics Engine</p>
            </div>
          </div>

          <div className="header-actions">
            {/* Live API status pill */}
            <span 
              className={`badge ${isLiveApi ? 'badge-success' : 'badge-neutral'}`}
              style={{ padding: '0.45rem 0.85rem', fontSize: '0.8rem' }}
              title={isLiveApi ? "Connected to live FastAPI backend on port 8000" : "Running on static compiled JSON"}
            >
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: isLiveApi ? '#10b981' : '#94a3b8' }} />
              {isLiveApi ? 'Live API Active' : 'Static Mode'}
            </span>

            {/* Run Analysis Button */}
            <button 
              className="btn btn-secondary"
              onClick={handleRunPipeline}
              disabled={isRefreshing}
            >
              <RefreshCw size={15} className={isRefreshing ? 'spin' : ''} />
              {isRefreshing ? 'Re-running...' : 'Re-run Analysis'}
            </button>

            {/* Download Excel Button */}
            <button 
              className="btn btn-primary"
              onClick={handleDownloadExcel}
            >
              <Download size={15} />
              Download Excel MIS
            </button>
          </div>
        </div>
      </header>

      {/* Temporary Feedback Notification Toast */}
      {feedbackMessage && (
        <div style={{
          backgroundColor: '#eff6ff',
          color: '#1e40af',
          borderBottom: '1px solid #bfdbfe',
          padding: '0.65rem 2rem',
          textAlign: 'center',
          fontSize: '0.85rem',
          fontWeight: 600,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '0.5rem'
        }}>
          <Sparkles size={16} />
          {feedbackMessage}
        </div>
      )}

      {/* Navigation Tabs */}
      <nav className="tabs-navigation-wrapper">
        <div className="tabs-navigation">
          <button 
            className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            <LayoutDashboard size={16} /> Executive Dashboard
          </button>

          <button 
            className={`tab-btn ${activeTab === 'dpd' ? 'active' : ''}`}
            onClick={() => setActiveTab('dpd')}
          >
            <BarChart3 size={16} /> DPD Aging Analysis
            <span className="tab-count-badge">{dpdBuckets.length}</span>
          </button>

          <button 
            className={`tab-btn ${activeTab === 'branch' ? 'active' : ''}`}
            onClick={() => setActiveTab('branch')}
          >
            <Building2 size={16} /> Branch Performance
            <span className="tab-count-badge">{branchPerformance.length}</span>
          </button>

          <button 
            className={`tab-btn ${activeTab === 'agency' ? 'active' : ''}`}
            onClick={() => setActiveTab('agency')}
          >
            <ShieldCheck size={16} /> Agency Scorecard
            <span className="tab-count-badge">{agencyPerformance.length}</span>
          </button>

          <button 
            className={`tab-btn ${activeTab === 'loans' ? 'active' : ''}`}
            onClick={() => setActiveTab('loans')}
          >
            <FileText size={16} /> Loan Register
            <span className="tab-count-badge">{loans.length}</span>
          </button>

          <button 
            className={`tab-btn ${activeTab === 'issues' ? 'active' : ''}`}
            onClick={() => setActiveTab('issues')}
          >
            <AlertTriangle size={16} /> Data Quality Audit
            <span className="tab-count-badge" style={{ backgroundColor: issues.length > 0 ? '#fef2f2' : '#f1f5f9', color: issues.length > 0 ? '#dc2626' : '#64748b' }}>
              {issues.length}
            </span>
          </button>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="main-content">
        {/* Tab 1: Executive Dashboard */}
        {activeTab === 'dashboard' && (
          <div>
            <KPICards kpis={kpis} />

            <div className="charts-grid">
              <DPDChart dpdBuckets={dpdBuckets} />
              <BranchChart branchPerformance={branchPerformance} />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(460px, 1fr))', gap: '1.5rem' }}>
              <DPDTable dpdBuckets={dpdBuckets} />
              <BranchTable branches={branchPerformance.slice(0, 5)} />
            </div>
          </div>
        )}

        {/* Tab 2: DPD Aging Analysis */}
        {activeTab === 'dpd' && (
          <div>
            <div className="charts-grid" style={{ gridTemplateColumns: '1fr' }}>
              <DPDChart dpdBuckets={dpdBuckets} />
            </div>
            <DPDTable dpdBuckets={dpdBuckets} />
          </div>
        )}

        {/* Tab 3: Branch Performance */}
        {activeTab === 'branch' && (
          <div>
            <div className="charts-grid" style={{ gridTemplateColumns: '1fr' }}>
              <BranchChart branchPerformance={branchPerformance} />
            </div>
            <BranchTable branches={branchPerformance} />
          </div>
        )}

        {/* Tab 4: Agency Performance */}
        {activeTab === 'agency' && (
          <div>
            <AgencyTable agencies={agencyPerformance} />
          </div>
        )}

        {/* Tab 5: Loan Register */}
        {activeTab === 'loans' && (
          <div>
            <div className="section-header">
              <div>
                <h2 className="section-title">Granular Loan Repayment & Delinquency Register</h2>
                <p className="section-subtitle">Real-time filtering, multi-criteria sorting, and risk classification</p>
              </div>
            </div>
            <LoanTable loans={loans} filters={filters} />
          </div>
        )}

        {/* Tab 6: Data Quality Audit */}
        {activeTab === 'issues' && (
          <div>
            <div className="section-header">
              <div>
                <h2 className="section-title">Data Quality Audit Log</h2>
                <p className="section-subtitle">Identified anomalies, primary key violations, negative balances, and corrective treatments</p>
              </div>
            </div>
            <IssuesTable issues={issues} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p><strong>LoanPulse Analytics — Automated Loan Collection & Delinquency MIS System</strong> | Personal Portfolio Project</p>
        <p style={{ marginTop: '0.25rem', fontSize: '0.75rem', color: '#94a3b8' }}>
          Built with Python, pandas, openpyxl & React • Generated at {data?.generated_at || 'Just now'}
        </p>
      </footer>
    </div>
  );
}
