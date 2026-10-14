import React from 'react';
import { AlertTriangle, ShieldAlert, CheckCircle } from 'lucide-react';

export default function IssuesTable({ issues }) {
  if (!issues || issues.length === 0) {
    return (
      <div className="table-container" style={{ padding: '3rem', textAlign: 'center' }}>
        <CheckCircle size={40} style={{ color: '#059669', marginBottom: '1rem' }} />
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Zero Data Quality Issues Detected</h3>
        <p style={{ color: '#64748b', fontSize: '0.85rem' }}>All ingested records passed data integrity and business validation rules.</p>
      </div>
    );
  }

  const criticalCount = issues.filter(i => i.severity === 'CRITICAL').length;
  const warningCount = issues.filter(i => i.severity === 'WARNING').length;

  return (
    <div>
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
        <div className="badge badge-danger" style={{ fontSize: '0.85rem', padding: '0.4rem 0.85rem' }}>
          <ShieldAlert size={16} /> {criticalCount} Critical Violations (Excluded from Core Portfolio)
        </div>
        <div className="badge badge-warning" style={{ fontSize: '0.85rem', padding: '0.4rem 0.85rem' }}>
          <AlertTriangle size={16} /> {warningCount} Warnings (Retained with Audit Flags)
        </div>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Row Index</th>
              <th>Loan ID</th>
              <th>Issue Type</th>
              <th className="text-center">Severity</th>
              <th>Issue Description</th>
              <th>Corrective Action Taken</th>
            </tr>
          </thead>
          <tbody>
            {issues.map((issue, idx) => (
              <tr key={idx}>
                <td style={{ color: '#64748b' }}>#{issue.record_index}</td>
                <td style={{ fontWeight: 700, color: '#1e3a8a' }}>{issue.loan_id}</td>
                <td style={{ fontWeight: 600 }}>{issue.issue_type}</td>
                <td className="text-center">
                  {issue.severity === 'CRITICAL' ? (
                    <span className="badge badge-danger">CRITICAL</span>
                  ) : (
                    <span className="badge badge-warning">WARNING</span>
                  )}
                </td>
                <td style={{ color: '#334155', maxWidth: '380px', whiteSpace: 'normal' }}>
                  {issue.description}
                </td>
                <td style={{ color: '#059669', fontWeight: 600, fontSize: '0.82rem' }}>
                  {issue.action_taken}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
