import React from 'react';
import { Landmark, TrendingUp, AlertCircle, CheckCircle2, Clock, IndianRupee } from 'lucide-react';

export default function KPICards({ kpis }) {
  if (!kpis) return null;

  const formatCurrency = (val) => {
    if (val === undefined || val === null) return '₹ 0';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(val);
  };

  const totalLoans = kpis['Total Active Loans'] || 0;
  const totalDue = kpis['Total Billing Due Amount'] || 0;
  const totalCollected = kpis['Total Amount Collected'] || 0;
  const totalOutstanding = kpis['Total Outstanding Amount'] || 0;
  const efficiency = kpis['Overall Collection Efficiency (%)'] || 0;
  const overpaidCount = kpis['Loans with Overpayment Flag'] || 0;

  return (
    <div className="kpi-grid">
      {/* KPI 1: Total Due */}
      <div className="kpi-card">
        <div className="kpi-header">
          <span className="kpi-label">Total Billing Due</span>
          <div className="kpi-icon-wrapper">
            <Landmark size={20} />
          </div>
        </div>
        <div className="kpi-value">{formatCurrency(totalDue)}</div>
        <div className="kpi-subtext">
          <span>Monthly Installments Due Across {totalLoans} Active Loans</span>
        </div>
      </div>

      {/* KPI 2: Total Collected */}
      <div className="kpi-card emerald">
        <div className="kpi-header">
          <span className="kpi-label">Cash Collected</span>
          <div className="kpi-icon-wrapper emerald">
            <CheckCircle2 size={20} />
          </div>
        </div>
        <div className="kpi-value" style={{ color: '#059669' }}>{formatCurrency(totalCollected)}</div>
        <div className="kpi-subtext">
          <span>Actual Realized Cash Recovery</span>
        </div>
      </div>

      {/* KPI 3: Total Outstanding */}
      <div className="kpi-card rose">
        <div className="kpi-header">
          <span className="kpi-label">Total Outstanding</span>
          <div className="kpi-icon-wrapper rose">
            <Clock size={20} />
          </div>
        </div>
        <div className="kpi-value" style={{ color: '#dc2626' }}>{formatCurrency(totalOutstanding)}</div>
        <div className="kpi-subtext">
          <span>Delinquent & Pending Portfolio Balance</span>
        </div>
      </div>

      {/* KPI 4: Collection Efficiency */}
      <div className="kpi-card amber">
        <div className="kpi-header">
          <span className="kpi-label">Collection Efficiency</span>
          <div className="kpi-icon-wrapper amber">
            <TrendingUp size={20} />
          </div>
        </div>
        <div className="kpi-value" style={{ color: '#d97706' }}>{efficiency.toFixed(1)}%</div>
        <div className="kpi-subtext">
          <span>Aggregated Cash Recovery Ratio</span>
        </div>
        <div className="progress-container">
          <div 
            className="progress-bar" 
            style={{ 
              width: `${Math.min(efficiency, 100)}%`, 
              backgroundColor: efficiency >= 80 ? '#059669' : efficiency >= 60 ? '#d97706' : '#dc2626' 
            }}
          />
        </div>
      </div>
    </div>
  );
}
