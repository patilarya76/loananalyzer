import React, { useState } from 'react';
import { BarChart3 } from 'lucide-react';

export default function DPDChart({ dpdBuckets }) {
  const [hoveredBucket, setHoveredBucket] = useState(null);

  if (!dpdBuckets || dpdBuckets.length === 0) return null;

  // Maximum value for scaling
  const maxOutstanding = Math.max(...dpdBuckets.map(b => b.total_outstanding || 0), 1);
  const totalOutstanding = dpdBuckets.reduce((acc, b) => acc + (b.total_outstanding || 0), 0);

  const getBucketColor = (bucketName) => {
    if (bucketName.includes('Current')) return '#10b981'; // Green
    if (bucketName.includes('Early')) return '#3b82f6';   // Blue
    if (bucketName.includes('Mid')) return '#f59e0b';     // Amber
    if (bucketName.includes('Late')) return '#ea580c';    // Orange
    if (bucketName.includes('90+')) return '#dc2626';     // Red
    return '#64748b';                                     // Slate
  };

  const formatLakhs = (amount) => {
    return `₹ ${(amount / 100000).toFixed(2)} L`;
  };

  return (
    <div className="chart-card">
      <div className="section-header" style={{ marginBottom: '1rem' }}>
        <div>
          <h3 className="section-title">
            <BarChart3 size={18} style={{ color: '#2563eb' }} />
            Outstanding Portfolio by DPD Bucket
          </h3>
          <p className="section-subtitle">Delinquency aging distribution across loan portfolio</p>
        </div>
        {hoveredBucket && (
          <div className="badge badge-info" style={{ fontSize: '0.8rem' }}>
            {hoveredBucket.dpd_bucket}: {formatLakhs(hoveredBucket.total_outstanding)} ({hoveredBucket.loan_count} loans)
          </div>
        )}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem', paddingTop: '0.5rem' }}>
        {dpdBuckets.map((bucket, idx) => {
          const widthPct = Math.max((bucket.total_outstanding / maxOutstanding) * 100, 2);
          const color = getBucketColor(bucket.dpd_bucket);
          const sharePct = totalOutstanding > 0 
            ? ((bucket.total_outstanding / totalOutstanding) * 100).toFixed(1)
            : 0;

          return (
            <div 
              key={idx}
              onMouseEnter={() => setHoveredBucket(bucket)}
              onMouseLeave={() => setHoveredBucket(null)}
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.25rem',
                cursor: 'pointer',
                padding: '0.35rem 0.5rem',
                borderRadius: '8px',
                backgroundColor: hoveredBucket?.dpd_bucket === bucket.dpd_bucket ? '#f8fafc' : 'transparent',
                transition: 'background 0.15s ease'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', fontWeight: 600 }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: color }} />
                  {bucket.dpd_bucket}
                </span>
                <span style={{ color: '#0f172a' }}>
                  {formatLakhs(bucket.total_outstanding)} <span style={{ color: '#64748b', fontWeight: 400 }}>({sharePct}%)</span>
                </span>
              </div>
              <div style={{ width: '100%', height: '18px', background: '#f1f5f9', borderRadius: '6px', overflow: 'hidden' }}>
                <div 
                  style={{
                    height: '100%',
                    width: `${widthPct}%`,
                    backgroundColor: color,
                    borderRadius: '6px',
                    transition: 'width 0.6s cubic-bezier(0.16, 1, 0.3, 1)',
                    display: 'flex',
                    alignItems: 'center',
                    paddingLeft: '6px',
                    color: '#ffffff',
                    fontSize: '0.68rem',
                    fontWeight: 700
                  }}
                >
                  {widthPct > 15 && `${bucket.loan_count} loans`}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
