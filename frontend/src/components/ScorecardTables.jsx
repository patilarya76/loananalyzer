import React from 'react';
import { Building2, ShieldCheck, Clock } from 'lucide-react';

const formatCurrency = (val) => {
  if (val === undefined || val === null) return '₹ 0';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(val);
};

export function BranchTable({ branches }) {
  if (!branches) return null;

  return (
    <div className="table-container">
      <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-light)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Building2 size={18} style={{ color: '#2563eb' }} />
        <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Branch Collection Performance Scorecard</h3>
      </div>
      <table className="data-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Branch Name</th>
            <th className="text-center">Loan Count</th>
            <th className="text-right">Billing Due Amount</th>
            <th className="text-right">Cash Collected</th>
            <th className="text-right">Outstanding Amount</th>
            <th style={{ width: '220px' }}>Collection Efficiency</th>
          </tr>
        </thead>
        <tbody>
          {branches.map((branch, idx) => {
            const eff = branch.collection_efficiency_pct || 0;
            const barColor = eff >= 80 ? '#059669' : eff >= 60 ? '#2563eb' : '#d97706';

            return (
              <tr key={branch.branch || idx}>
                <td style={{ fontWeight: 700, color: '#64748b' }}>#{idx + 1}</td>
                <td style={{ fontWeight: 700, color: '#0f172a' }}>{branch.branch}</td>
                <td className="text-center">{branch.loan_count}</td>
                <td className="text-right">{formatCurrency(branch.total_due)}</td>
                <td className="text-right" style={{ color: '#059669', fontWeight: 600 }}>{formatCurrency(branch.total_collected)}</td>
                <td className="text-right" style={{ color: '#dc2626', fontWeight: 600 }}>{formatCurrency(branch.total_outstanding)}</td>
                <td>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 700, color: barColor }}>
                    <span>{eff.toFixed(1)}%</span>
                  </div>
                  <div className="progress-container">
                    <div 
                      className="progress-bar" 
                      style={{ width: `${Math.min(eff, 100)}%`, backgroundColor: barColor }} 
                    />
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export function AgencyTable({ agencies }) {
  if (!agencies) return null;

  return (
    <div className="table-container">
      <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-light)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <ShieldCheck size={18} style={{ color: '#059669' }} />
        <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Collection Agency & Internal Team Scorecard</h3>
      </div>
      <table className="data-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Collection Agency / Team</th>
            <th className="text-center">Accounts Handled</th>
            <th className="text-right">Billing Due Amount</th>
            <th className="text-right">Recovered Amount</th>
            <th className="text-right">Pending Balance</th>
            <th style={{ width: '220px' }}>Recovery Efficiency</th>
          </tr>
        </thead>
        <tbody>
          {agencies.map((agency, idx) => {
            const eff = agency.collection_efficiency_pct || 0;
            const barColor = eff >= 80 ? '#059669' : eff >= 60 ? '#2563eb' : '#d97706';

            return (
              <tr key={agency.collection_agency || idx}>
                <td style={{ fontWeight: 700, color: '#64748b' }}>#{idx + 1}</td>
                <td style={{ fontWeight: 700, color: '#0f172a' }}>{agency.collection_agency}</td>
                <td className="text-center">{agency.loan_count}</td>
                <td className="text-right">{formatCurrency(agency.total_due)}</td>
                <td className="text-right" style={{ color: '#059669', fontWeight: 600 }}>{formatCurrency(agency.total_collected)}</td>
                <td className="text-right" style={{ color: '#dc2626', fontWeight: 600 }}>{formatCurrency(agency.total_outstanding)}</td>
                <td>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', fontWeight: 700, color: barColor }}>
                    <span>{eff.toFixed(1)}%</span>
                  </div>
                  <div className="progress-container">
                    <div 
                      className="progress-bar" 
                      style={{ width: `${Math.min(eff, 100)}%`, backgroundColor: barColor }} 
                    />
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export function DPDTable({ dpdBuckets }) {
  if (!dpdBuckets) return null;

  return (
    <div className="table-container">
      <div style={{ padding: '1rem 1.25rem', borderBottom: '1px solid var(--border-light)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <Clock size={18} style={{ color: '#f59e0b' }} />
        <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Delinquency Aging Portfolio Summary</h3>
      </div>
      <table className="data-table">
        <thead>
          <tr>
            <th>Delinquency Bucket</th>
            <th className="text-center">Loan Count</th>
            <th className="text-right">Billing Due Amount</th>
            <th className="text-right">Amount Collected</th>
            <th className="text-right">Outstanding Amount</th>
            <th className="text-right">Recovery Rate (%)</th>
            <th className="text-right">Share of Delinquency (%)</th>
          </tr>
        </thead>
        <tbody>
          {dpdBuckets.map((bucket, idx) => (
            <tr key={bucket.dpd_bucket || idx}>
              <td style={{ fontWeight: 700 }}>{bucket.dpd_bucket}</td>
              <td className="text-center">{bucket.loan_count}</td>
              <td className="text-right">{formatCurrency(bucket.total_due)}</td>
              <td className="text-right" style={{ color: '#059669', fontWeight: 600 }}>{formatCurrency(bucket.total_collected)}</td>
              <td className="text-right" style={{ color: '#dc2626', fontWeight: 700 }}>{formatCurrency(bucket.total_outstanding)}</td>
              <td className="text-right" style={{ fontWeight: 600 }}>{bucket.collection_efficiency_pct.toFixed(1)}%</td>
              <td className="text-right" style={{ fontWeight: 600, color: '#475569' }}>{bucket.share_of_outstanding_pct.toFixed(1)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
