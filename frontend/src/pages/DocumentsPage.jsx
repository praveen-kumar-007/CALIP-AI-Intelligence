import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';

export function DocumentsPage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDocuments() {
      try {
        setLoading(true);
        const data = await api.getDocuments('', '', 100);
        setDocuments(Array.isArray(data) ? data : data?.documents || data?.items || []);
      } catch (err) {
        console.error('Failed loading documents:', err);
      } finally {
        setLoading(false);
      }
    }
    loadDocuments();
  }, []);

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '2rem', flexWrap: 'wrap', gap: '1.25rem' }}>
        <div>
          <div className="hero-pill" style={{ marginBottom: '0.5rem' }}>Verified Legal Repository</div>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--text-pure)', marginBottom: '0.5rem' }}>
            Legal Documents &amp; OCR Archive
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>
            Archive of all ingested legal PDF files, FIRs, charge sheets, trial exhibits, and court filings with page-by-page OCR extraction and separate RAG text storage.
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

      <div className="category-block" style={{ marginBottom: '3.5rem' }}>
        <div style={{ padding: '1rem 1.5rem', background: 'rgba(255, 255, 255, 0.02)', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
          <span style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
            Showing <strong style={{ color: 'var(--text-pure)' }}>{documents.length}</strong> documents in database
          </span>
          <span style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)' }}>
            &bull; Indexed &amp; stored in PostgreSQL (Supabase)
          </span>
        </div>

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
            {documents.map((doc) => (
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
      </div>
    </>
  );
}
