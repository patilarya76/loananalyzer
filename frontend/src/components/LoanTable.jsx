import React, { useState, useMemo } from 'react';
import { Search, Filter, ArrowUpDown, ChevronLeft, ChevronRight, FileSpreadsheet } from 'lucide-react';

export default function LoanTable({ loans, filters }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBranch, setSelectedBranch] = useState('ALL');
  const [selectedAgency, setSelectedAgency] = useState('ALL');
  const [selectedBucket, setSelectedBucket] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  
  const [sortField, setSortField] = useState('days_past_due');
  const [sortDirection, setSortDirection] = useState('desc'); // 'asc' or 'desc'
  
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 12;

  // Filter and Sort Logic
  const filteredLoans = useMemo(() => {
    if (!loans) return [];

    return loans.filter((loan) => {
      // Search term
      const term = searchTerm.toLowerCase();
      const matchesSearch = 
        !term ||
        loan.loan_id?.toLowerCase().includes(term) ||
        loan.customer_name?.toLowerCase().includes(term) ||
        loan.branch?.toLowerCase().includes(term);

      // Dropdown filters
      const matchesBranch = selectedBranch === 'ALL' || loan.branch === selectedBranch;
      const matchesAgency = selectedAgency === 'ALL' || loan.collection_agency === selectedAgency;
      const matchesBucket = selectedBucket === 'ALL' || loan.dpd_bucket === selectedBucket;
      const matchesStatus = selectedStatus === 'ALL' || loan.payment_status === selectedStatus;

      return matchesSearch && matchesBranch && matchesAgency && matchesBucket && matchesStatus;
    }).sort((a, b) => {
      let aVal = a[sortField];
      let bVal = b[sortField];

      if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = bVal.toLowerCase();
      }

      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [loans, searchTerm, selectedBranch, selectedAgency, selectedBucket, selectedStatus, sortField, sortDirection]);

  // Pagination slice
  const totalPages = Math.ceil(filteredLoans.length / pageSize) || 1;
  const paginatedLoans = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredLoans.slice(start, start + pageSize);
  }, [filteredLoans, currentPage, pageSize]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
    setCurrentPage(1);
  };

  const formatCurrency = (val) => {
    if (val === undefined || val === null) return '₹ 0';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(val);
  };

  const getStatusBadge = (status, isOverpaid) => {
    if (isOverpaid) {
      return <span className="badge badge-warning">Overpaid</span>;
    }
    switch (status) {
      case 'Fully Paid':
        return <span className="badge badge-success">Fully Paid</span>;
      case 'Partially Paid':
        return <span className="badge badge-warning">Partially Paid</span>;
      case 'Unpaid':
        return <span className="badge badge-danger">Unpaid</span>;
      default:
        return <span className="badge badge-neutral">{status || 'Pending'}</span>;
    }
  };

  const getDPDBadge = (dpd, bucket) => {
    if (dpd === 0) {
      return <span className="badge badge-success">0 DPD</span>;
    } else if (dpd <= 30) {
      return <span className="badge badge-info">{dpd} DPD</span>;
    } else if (dpd <= 60) {
      return <span className="badge badge-warning">{dpd} DPD</span>;
    } else {
      return <span className="badge badge-danger">{dpd} DPD</span>;
    }
  };

  return (
    <div>
      {/* Filters Toolbar */}
      <div className="filters-bar">
        <div className="search-box">
          <Search size={16} className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search by Loan ID, Customer Name, or Branch..."
            value={searchTerm}
            onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
          />
        </div>

        {/* Branch Filter */}
        <select 
          className="filter-select"
          value={selectedBranch}
          onChange={(e) => { setSelectedBranch(e.target.value); setCurrentPage(1); }}
        >
          <option value="ALL">All Branches</option>
          {filters?.branches?.map((b) => (
            <option key={b} value={b}>{b}</option>
          ))}
        </select>

        {/* Agency Filter */}
        <select 
          className="filter-select"
          value={selectedAgency}
          onChange={(e) => { setSelectedAgency(e.target.value); setCurrentPage(1); }}
        >
          <option value="ALL">All Agencies</option>
          {filters?.agencies?.map((a) => (
            <option key={a} value={a}>{a}</option>
          ))}
        </select>

        {/* DPD Bucket Filter */}
        <select 
          className="filter-select"
          value={selectedBucket}
          onChange={(e) => { setSelectedBucket(e.target.value); setCurrentPage(1); }}
        >
          <option value="ALL">All DPD Buckets</option>
          {filters?.dpd_buckets?.map((bucket) => (
            <option key={bucket} value={bucket}>{bucket}</option>
          ))}
        </select>

        {/* Payment Status Filter */}
        <select 
          className="filter-select"
          value={selectedStatus}
          onChange={(e) => { setSelectedStatus(e.target.value); setCurrentPage(1); }}
        >
          <option value="ALL">All Statuses</option>
          {filters?.payment_statuses?.map((st) => (
            <option key={st} value={st}>{st}</option>
          ))}
        </select>
      </div>

      {/* Table Component */}
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('loan_id')} style={{ cursor: 'pointer' }}>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  Loan ID <ArrowUpDown size={12} />
                </span>
              </th>
              <th onClick={() => handleSort('customer_name')} style={{ cursor: 'pointer' }}>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                  Customer Name <ArrowUpDown size={12} />
                </span>
              </th>
              <th>Branch</th>
              <th>Agency</th>
              <th className="text-right" onClick={() => handleSort('loan_amount')} style={{ cursor: 'pointer' }}>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', justifyContent: 'flex-end' }}>
                  Principal <ArrowUpDown size={12} />
                </span>
              </th>
              <th className="text-right" onClick={() => handleSort('due_amount')} style={{ cursor: 'pointer' }}>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', justifyContent: 'flex-end' }}>
                  Due Amount <ArrowUpDown size={12} />
                </span>
              </th>
              <th className="text-right" onClick={() => handleSort('paid_amount')} style={{ cursor: 'pointer' }}>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', justifyContent: 'flex-end' }}>
                  Paid Amount <ArrowUpDown size={12} />
                </span>
              </th>
              <th className="text-right" onClick={() => handleSort('outstanding_amount')} style={{ cursor: 'pointer' }}>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', justifyContent: 'flex-end' }}>
                  Outstanding <ArrowUpDown size={12} />
                </span>
              </th>
              <th className="text-center" onClick={() => handleSort('days_past_due')} style={{ cursor: 'pointer' }}>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', justifyContent: 'center' }}>
                  DPD <ArrowUpDown size={12} />
                </span>
              </th>
              <th className="text-center">Status</th>
            </tr>
          </thead>
          <tbody>
            {paginatedLoans.length === 0 ? (
              <tr>
                <td colSpan={10} style={{ textAlign: 'center', padding: '2.5rem', color: '#64748b' }}>
                  No loan records match your current filter criteria.
                </td>
              </tr>
            ) : (
              paginatedLoans.map((loan, idx) => (
                <tr key={loan.loan_id || idx}>
                  <td style={{ fontWeight: 700, color: '#1e3a8a' }}>{loan.loan_id}</td>
                  <td style={{ fontWeight: 600 }}>{loan.customer_name}</td>
                  <td>{loan.branch}</td>
                  <td style={{ color: '#475569', fontSize: '0.82rem' }}>{loan.collection_agency}</td>
                  <td className="text-right">{formatCurrency(loan.loan_amount)}</td>
                  <td className="text-right" style={{ fontWeight: 600 }}>{formatCurrency(loan.due_amount)}</td>
                  <td className="text-right" style={{ color: '#059669', fontWeight: 600 }}>{formatCurrency(loan.paid_amount)}</td>
                  <td className="text-right" style={{ color: loan.outstanding_amount > 0 ? '#dc2626' : '#64748b', fontWeight: 700 }}>
                    {formatCurrency(loan.outstanding_amount)}
                  </td>
                  <td className="text-center">{getDPDBadge(loan.days_past_due, loan.dpd_bucket)}</td>
                  <td className="text-center">{getStatusBadge(loan.payment_status, loan.overpayment_flag)}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>

        {/* Pagination Bar */}
        <div className="pagination-bar">
          <div>
            Showing <strong>{filteredLoans.length > 0 ? (currentPage - 1) * pageSize + 1 : 0}</strong> to <strong>{Math.min(currentPage * pageSize, filteredLoans.length)}</strong> of <strong>{filteredLoans.length}</strong> matching loans
          </div>
          <div className="pagination-controls">
            <button 
              className="btn btn-secondary" 
              style={{ padding: '0.35rem 0.65rem' }}
              disabled={currentPage <= 1}
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
            >
              <ChevronLeft size={16} /> Previous
            </button>
            <span style={{ display: 'flex', alignItems: 'center', padding: '0 0.5rem', fontWeight: 600 }}>
              Page {currentPage} of {totalPages}
            </span>
            <button 
              className="btn btn-secondary" 
              style={{ padding: '0.35rem 0.65rem' }}
              disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
            >
              Next <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
