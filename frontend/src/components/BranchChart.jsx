import React, { useState } from 'react';
import { Building2 } from 'lucide-react';

export default function BranchChart({ branchPerformance }) {
  const [hoveredBranch, setHoveredBranch] = useState(null);

  if (!branchPerformance || branchPerformance.length === 0) return null;

  // Sorted branches by efficiency descending
  const sortedBranches = [...branchPerformance].sort((a, b) => b.collection_efficiency_pct - a.collection_efficiency_pct);

  return (
    <div className="chart-card">
      <div className="section-header" style={{ marginBottom: '1rem' }}>
        <div>
          <h3 className="section-title">
            <Building2 size={18} style={{ color: '#059669' }} />
            Branch Collection Efficiency (%)
          </h3>
          <p className="section-subtitle">Ranked recovery performance vs 80% benchmark target</p>
        </div>
        {hoveredBranch && (
          <div className="badge badge-success" style={{ fontSize: '0.8rem' }}>
            {hoveredBranch.branch}: {hoveredBranch.collection_efficiency_pct.toFixed(1)}% ({hoveredBranch.loan_count} loans)
          </div>
        )}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', paddingTop: '0.5rem' }}>
        {sortedBranches.map((item, idx) => {
          const efficiency = item.collection_efficiency_pct || 0;
          const isAboveTarget = efficiency >= 80;
          const barColor = isAboveTarget ? '#059669' : efficiency >= 60 ? '#2563eb' : '#d97706';

          return (
            <div 
              key={idx}
              onMouseEnter={() => setHoveredBranch(item)}
              onMouseLeave={() => setHoveredBranch(null)}
              style={{
                display: 'flex',
                flexDirection: 'column',
                gap: '0.2rem',
                cursor: 'pointer',
                padding: '0.25rem 0.5rem',
                borderRadius: '8px',
                backgroundColor: hoveredBranch?.branch === item.branch ? '#f8fafc' : 'transparent',
                transition: 'background 0.15s ease'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', fontWeight: 600 }}>
                <span>{item.branch}</span>
                <span style={{ color: barColor, fontWeight: 700 }}>
                  {efficiency.toFixed(1)}% <span style={{ color: '#64748b', fontWeight: 400 }}>({item.loan_count} loans)</span>
                </span>
              </div>
              <div style={{ width: '100%', height: '14px', background: '#f1f5f9', borderRadius: '4px', overflow: 'hidden', position: 'relative' }}>
                {/* 80% Target Benchmark marker */}
                <div 
                  style={{
                    position: 'absolute',
                    left: '80%',
                    top: 0,
                    bottom: 0,
                    width: '2px',
                    backgroundColor: '#dc2626',
                    zIndex: 2,
                    opacity: 0.75
                  }}
                  title="80% Benchmark Target"
                />
                <div 
                  style={{
                    height: '100%',
                    width: `${Math.min(efficiency, 100)}%`,
                    backgroundColor: barColor,
                    borderRadius: '4px',
                    transition: 'width 0.6s cubic-bezier(0.16, 1, 0.3, 1)'
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginTop: '1rem', fontSize: '0.75rem', color: '#64748b' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#059669' }} /> ≥ 80% Target
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#2563eb' }} /> 60% – 79% Moderate
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#d97706' }} /> &lt; 60% Needs Follow-up
        </span>
      </div>
    </div>
  );
}
