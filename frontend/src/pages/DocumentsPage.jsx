import React, { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';

export function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(50);

  useEffect(() => {
    async function loadDocuments() {
      try {
        setLoading(true);
        const data = await api.getDocuments('', '', 1000);
        const docList = Array.isArray(data) ? data : data?.documents || data?.items || [];
        setDocuments(docList);
        setTotalCount(data?.total || docList.length);
      } catch (err) {
        console.error('Failed loading documents:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDocuments();
  }, []);

  const filteredDocs = useMemo(() => {
    return documents.filter((doc) => {
      const matchSearch =
        !searchTerm.trim() ||
        (doc.title && doc.title.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (doc.case_number && doc.case_number.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (doc.court && doc.court.toLowerCase().includes(searchTerm.toLowerCase())) ||
        (doc.id && doc.id.toLowerCase().includes(searchTerm.toLowerCase()));

      const matchType =
        !typeFilter ||
        (doc.document_type && doc.document_type.toLowerCase() === typeFilter.toLowerCase());

      return matchSearch && matchType;
    });
  }, [documents, searchTerm, typeFilter]);

  const totalPages = pageSize === 'all' ? 1 : Math.ceil(filteredDocs.length / pageSize);

  const displayedDocs = useMemo(() => {
    if (pageSize === 'all') return filteredDocs;
    const start = (currentPage - 1) * pageSize;
    return filteredDocs.slice(start, start + pageSize);
  }, [filteredDocs, currentPage, pageSize]);

  // Reset to page 1 if filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, typeFilter, pageSize]);

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '2rem', flexWrap: 'wrap', gap: '1.25rem' }}>
        <div>
          <div className="hero-pill" style={{ marginBottom: '0.5rem' }}>Verified Legal Repository</div>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--text-pure)', marginBottom: '0.5rem' }}>
            Legal Documents &amp; OCR Archive
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>
            Authoritative catalog of all {totalCount || documents.length} legal records from longtailcases.com with cryptographic hashes, verified OCR, and structured text exports.
          </p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Link to="/admin" className="btn btn-primary btn-sm">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="17 8 12 3 7 8"/>
              <line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            Upload &amp; Ingest PDF
          </Link>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ flex: '1', minWidth: '280px' }}>
          <input
            type="text"
            className="search-input"
            style={{ width: '100%', padding: '0.7rem 1.2rem', fontSize: '0.9rem' }}
            placeholder="Search across all 800+ documents by title, case number, court, or ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
          <select
            className="search-input"
            style={{ padding: '0.65rem 1rem', fontSize: '0.85rem' }}
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
          >
            <option value="">All Document Types</option>
            <option value="Document">General Document</option>
            <option value="ChargeSheet">Charge Sheet</option>
            <option value="FIR">FIR Record</option>
            <option value="Order">Court Order</option>
            <option value="Judgment">Judgment</option>
            <option value="Application">Application</option>
          </select>

          <select
            className="search-input"
            style={{ padding: '0.65rem 1rem', fontSize: '0.85rem' }}
            value={pageSize}
            onChange={(e) => setPageSize(e.target.value === 'all' ? 'all' : Number(e.target.value))}
          >
            <option value={50}>50 per page</option>
            <option value={100}>100 per page</option>
            <option value={250}>250 per page</option>
            <option value="all">Show All ({filteredDocs.length})</option>
          </select>
        </div>
      </div>

      <div className="category-block" style={{ marginBottom: '3.5rem' }}>
        <div style={{ padding: '1rem 1.5rem', background: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
          <span style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
            Showing <strong style={{ color: 'var(--text-pure)' }}>{displayedDocs.length}</strong> of{' '}
            <strong style={{ color: 'var(--text-pure)' }}>{filteredDocs.length}</strong> matched{' '}
            (Total <strong style={{ color: 'var(--accent-cyan)' }}>{totalCount || documents.length}</strong> in Supabase Database)
          </span>
          <span style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)' }}>
            &bull; Connected to Supabase PostgreSQL &bull; Full Catalog from longtailcases.com
          </span>
        </div>

        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            Loading legal documents repository from database...
          </div>
        ) : (
          <table className="detail-table">
            <thead>
              <tr>
                <th>Document Title</th>
                <th>Case / FIR #</th>
                <th>Type</th>
                <th>Court</th>
                <th>Pages</th>
                <th>Storage &amp; OCR Engine</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {displayedDocs.map((doc) => (
                <tr key={doc.id}>
                  <td>
                    <Link to={`/documents/${doc.id}`} style={{ fontWeight: 700, color: 'var(--text-pure)', fontSize: '0.92rem' }}>
                      {doc.title}
                    </Link>
                    {doc.has_txt && (
                      <div style={{ marginTop: '0.25rem' }}>
                        <span className="action-status-badge">&#10003; Separately Stored TXT</span>
                      </div>
                    )}
                  </td>
                  <td>
                    {doc.case_id ? (
                      <Link to={`/cases/${doc.case_id}`} className="badge badge-indigo" title={doc.case_title || 'View Case'}>
                        {doc.case_number || 'Case Link'}
                      </Link>
                    ) : (
                      <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>Direct Ingest</span>
                    )}
                  </td>
                  <td><span className="badge badge-indigo">{doc.document_type || 'Document'}</span></td>
                  <td style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{doc.court || 'District Court'}</td>
                  <td><strong style={{ color: 'var(--text-pure)' }}>{doc.page_count || 1}</strong></td>
                  <td>
                    <span className={`badge ${doc.ocr_status === 'completed' ? 'badge-emerald' : 'badge-cyan'}`}>
                      {doc.extraction_method || 'pymupdf_text'}
                    </span>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.2rem', fontFamily: 'var(--font-mono)' }}>
                      {doc.file_hash ? `${doc.file_hash.substring(0, 12)}...` : 'SHA-256'}
                    </div>
                  </td>
                  <td style={{ whiteSpace: 'nowrap' }}>
                    <div className="doc-actions-group">
                      {(doc.original_pdf_url || doc.pdf_url) && (
                        <a href={doc.original_pdf_url || doc.pdf_url} target="_blank" rel="noreferrer" className="action-pill action-pill-pdf" title="View or Download Original PDF">
                          PDF &nearr;
                        </a>
                      )}
                      <Link to={`/documents/${doc.id}#tab-extracted-text`} className="action-pill action-pill-ocr" title="Inspect OCR & Extracted Text">
                        OCR
                      </Link>
                      <a href={`/documents/${doc.id}/download/txt`} className="action-pill action-pill-txt" title="Download Clean Plain Text (.txt)">
                        TXT &darr;
                      </a>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {/* Pagination bar */}
        {pageSize !== 'all' && totalPages > 1 && (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 1.5rem', borderTop: '1px solid var(--border-subtle)', flexWrap: 'wrap', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Page {currentPage} of {totalPages}
            </span>
            <div style={{ display: 'flex', gap: '0.4rem' }}>
              <button
                className="btn btn-secondary btn-sm"
                disabled={currentPage === 1}
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              >
                &larr; Previous
              </button>
              <button
                className="btn btn-secondary btn-sm"
                disabled={currentPage >= totalPages}
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              >
                Next &rarr;
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
