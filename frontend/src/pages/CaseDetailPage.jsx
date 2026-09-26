import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';

export function CaseDetailPage() {
  const { id } = useParams();
  const [caseItem, setCaseItem] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCase() {
      try {
        setLoading(true);
        const data = await api.getCaseById(id);
        setCaseItem(data);
      } catch (err) {
        console.error('Error loading case:', err);
      } finally {
        setLoading(false);
      }
    }
    if (id) loadCase();
  }, [id]);

  if (loading) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        Loading case dossier...
      </div>
    );
  }

  if (!caseItem) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center' }}>
        <h2>Case Record Not Found</h2>
        <Link to="/cases" className="btn btn-primary" style={{ marginTop: '1rem' }}>
          Back to Cases
        </Link>
      </div>
    );
  }

  const docs = caseItem.documents || [];
  const folderTree = caseItem.folder_tree || [];
  const linkages = caseItem.linkages || null;

  return (
    <>
      {/* Breadcrumb */}
      <nav style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: '0.85rem', color: 'var(--text-dim)' }}>
        <Link to="/" style={{ color: 'var(--text-dim)' }}>Home</Link>
        <span>/</span>
        <Link to="/cases" style={{ color: 'var(--text-dim)' }}>Cases</Link>
        <span>/</span>
        <span style={{ color: 'var(--accent-cyan)' }}>{caseItem.case_number}</span>
      </nav>

      {/* Case Header Card */}
      <div className="category-block" style={{ padding: '2rem', marginBottom: '2rem', background: 'var(--bg-card)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
          <div>
            <span className="badge badge-indigo" style={{ marginBottom: '0.5rem' }}>
              {caseItem.subject || 'Case Record'}
            </span>
            <h1 style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
              {caseItem.title}
            </h1>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
              <span>Court: <strong style={{ color: 'var(--text-main)' }}>{caseItem.court || 'District Court'}</strong></span> &bull;
              <span>Bench: <strong style={{ color: 'var(--text-main)' }}>{caseItem.bench || 'Regular Bench'}</strong></span> &bull;
              <span>Filing Date: <strong style={{ color: 'var(--text-main)' }}>{caseItem.filing_date || 'Recorded'}</strong></span> &bull;
              <span>Status: <span className="badge badge-emerald">{(caseItem.status || 'Active').toUpperCase()}</span></span>
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            <Link
              to={`/ai-research?query=${encodeURIComponent(`What are the main facts and proceedings in case ${caseItem.case_number}?`)}`}
              className="btn btn-primary btn-sm"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>
              </svg>
              Ask AI About Case
            </Link>
            {caseItem.source_url && (
              <a href={caseItem.source_url} target="_blank" rel="noreferrer" className="btn btn-secondary btn-sm">
                Original Source &nearr;
              </a>
            )}
          </div>
        </div>

        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', lineHeight: 1.6, borderTop: '1px solid var(--border-subtle)', paddingTop: '1.25rem' }}>
          {caseItem.summary || 'Official case docket preserving proceedings, evidence documents, exhibits, orders, and filings.'}
        </p>
      </div>

      {/* Case Metadata Grid */}
      <div className="card-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', marginBottom: '2.5rem' }}>
        {/* Details */}
        <div className="legal-card">
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-pure)', marginBottom: '0.5rem' }}>Statutory &amp; Docket Info</h3>
          <table className="detail-table">
            <tbody>
              <tr>
                <th>Unique Case Number</th>
                <td><code style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)', fontWeight: 700 }}>{caseItem.case_number}</code></td>
              </tr>
              {linkages && linkages.primary_fir_number && (
                <tr>
                  <th>Linked FIR Number</th>
                  <td>
                    <span className="badge badge-rose" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>
                      FIR {linkages.primary_fir_number}
                    </span>
                  </td>
                </tr>
              )}
              <tr>
                <th>Case Type</th>
                <td>{caseItem.case_type || 'Criminal / Civil Dispute'}</td>
              </tr>
              <tr>
                <th>Jurisdiction / PS</th>
                <td>{caseItem.court || 'General Legal Jurisdiction'}</td>
              </tr>
              <tr>
                <th>Applicable Acts</th>
                <td>{caseItem.acts || 'IPC, CrPC, Special State Enactments'}</td>
              </tr>
            </tbody>
          </table>
        </div>

        {/* Documents Summary */}
        <div className="legal-card">
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-pure)', marginBottom: '0.5rem' }}>Archive &amp; Ingestion Statistics</h3>
          <table className="detail-table">
            <tbody>
              <tr>
                <th>Total Documents</th>
                <td><strong>{docs.length}</strong> files cataloged</td>
              </tr>
              <tr>
                <th>Hierarchical Folders</th>
                <td><strong>{folderTree.length}</strong> longtail folders</td>
              </tr>
              <tr>
                <th>Canonical URL</th>
                <td><code style={{ fontSize: '0.8rem' }}>{caseItem.canonical_url || `/cases/${caseItem.id}`}</code></td>
              </tr>
              <tr>
                <th>Provenance</th>
                <td>Cryptographic SHA-256 verified</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* UNIQUE CASE & FIR LINKAGE PANEL */}
      {linkages && (
        <div className="linkage-card" style={{ marginBottom: '2.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '0.75rem' }}>
            <div>
              <div className="hero-pill" style={{ marginBottom: '0.3rem' }}>Automatic Docket &amp; FIR Correlation</div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--text-pure)' }}>
                Unique FIR Copies, Charge Sheets &amp; Connected Cases
              </h3>
            </div>
            <span className="badge badge-emerald">Linked by Unique ID: {linkages.primary_fir_number || caseItem.case_number}</span>
          </div>

          {/* 1. Dedicated FIR Copies */}
          {linkages.fir_copies && linkages.fir_copies.length > 0 && (
            <div style={{ marginBottom: '1.5rem' }}>
              <h4 style={{ fontSize: '0.92rem', fontBold: 700, color: 'var(--text-pure)', marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: '#e11d48' }}>
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                  <polyline points="14 2 14 8 20 8"/>
                </svg>
                Primary Registered FIR Copy (Unique Investigation Provenance)
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {linkages.fir_copies.map((fir, idx) => (
                  <div key={idx} style={{ background: 'rgba(255, 255, 255, 0.9)', border: '1px solid rgba(225, 29, 72, 0.2)', borderRadius: 'var(--radius-md)', padding: '0.75rem 1.15rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem', boxShadow: '0 2px 6px rgba(225, 29, 72, 0.04)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                      <span className="badge badge-rose">{fir.language || 'Official'} FIR</span>
                      <Link to={`/documents/${fir.id}`} style={{ fontWeight: 700, color: 'var(--text-pure)', fontSize: '0.92rem' }}>
                        {fir.title}
                      </Link>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>&bull; Folder: {fir.folder_name}</span>
                    </div>
                    <div className="doc-actions-group">
                      {fir.url && (
                        <a href={fir.url} target="_blank" rel="noreferrer" className="action-pill action-pill-pdf" title="View Source PDF">PDF &nearr;</a>
                      )}
                      <Link to={`/documents/${fir.id}#tab-extracted-text`} className="action-pill action-pill-ocr">OCR</Link>
                      <a href={`/documents/${fir.id}/download/txt`} className="action-pill action-pill-txt">TXT &darr;</a>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 2. Connected Cases */}
          {linkages.connected_cases && linkages.connected_cases.length > 0 && (
            <div style={{ marginBottom: '1.25rem' }}>
              <h4 style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-pure)', marginBottom: '0.6rem' }}>
                Connected Cases &amp; Co-Arising Proceedings
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '0.75rem' }}>
                {linkages.connected_cases.map((cc, idx) => (
                  <div key={idx} style={{ background: 'rgba(248, 250, 252, 0.9)', border: '1px solid rgba(0, 0, 0, 0.06)', borderRadius: 'var(--radius-sm)', padding: '0.75rem 1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.25rem' }}>
                      <code style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)', fontWeight: 700, fontSize: '0.82rem' }}>{cc.case_number}</code>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{cc.doc_count || 0} files</span>
                    </div>
                    <Link to={`/cases/${cc.id}`} style={{ fontWeight: 600, color: 'var(--text-pure)', fontSize: '0.88rem', display: 'block', marginBottom: '0.25rem' }}>
                      {cc.title}
                    </Link>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {cc.relation_reason || 'Connected docket under same crime station.'}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Hierarchical Document Tree */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '0.75rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-pure)' }}>Case Folders &amp; Document Files</h2>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
            Exact hierarchical folder structure matching longtailcases.com repository with instant PDF, OCR, and TXT access.
          </p>
        </div>
      </div>

      <div className="category-block" style={{ padding: '1.5rem', marginBottom: '3rem' }}>
        {folderTree && folderTree.length > 0 ? (
          <div className="folder-tree" style={{ marginLeft: 0, borderLeft: 'none', paddingLeft: 0 }}>
            {folderTree.map((folder, fIdx) => (
              <div className="folder-item" key={fIdx} style={{ marginBottom: '1.25rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.85rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                  <span style={{ fontWeight: 700, color: 'var(--text-pure)', fontSize: '1.05rem', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--accent-indigo)' }}>
                      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                    </svg>
                    {folder.title}
                  </span>
                  <span className="badge badge-indigo">{(folder.documents || []).length} files</span>
                </div>

                {/* Top-Level Folder Documents */}
                {folder.documents && folder.documents.length > 0 && (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem', marginBottom: '1rem' }}>
                    {folder.documents.map((doc, dIdx) => (
                      <div key={dIdx} className="doc-link-item" style={{ background: 'rgba(255, 255, 255, 0.88)', border: '1px solid rgba(0, 0, 0, 0.06)', padding: '0.65rem 0.95rem', borderRadius: 'var(--radius-sm)', boxShadow: '0 1px 3px rgba(0,0,0,0.02)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.6rem' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--accent-rose)' }}>
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14 2 14 8 20 8"/>
                          </svg>
                          <Link to={`/documents/${doc.id}`} style={{ fontWeight: 600, color: 'var(--text-pure)', fontSize: '0.9rem' }}>
                            {doc.title}
                          </Link>
                        </span>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          {doc.has_txt && <span className="action-status-badge">&#10003; TXT Ready</span>}
                          <div className="doc-actions-group">
                            {doc.url && (
                              <a href={doc.url} target="_blank" rel="noreferrer" className="action-pill action-pill-pdf" title="View Source PDF Document">
                                PDF &nearr;
                              </a>
                            )}
                            <Link to={`/documents/${doc.id}#tab-extracted-text`} className="action-pill action-pill-ocr" title="Inspect Advanced OCR & Layout">
                              OCR
                            </Link>
                            <a href={`/documents/${doc.id}/download/txt`} className="action-pill action-pill-txt" title="Download Plain Extracted Text (.txt)">
                              TXT &darr;
                            </a>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          /* Flat Documents Fallback if no folderTree */
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {docs.map((doc) => (
              <div key={doc.id} className="doc-link-item" style={{ background: 'rgba(255, 255, 255, 0.88)', border: '1px solid rgba(0, 0, 0, 0.06)', padding: '0.65rem 0.95rem', borderRadius: 'var(--radius-sm)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.6rem' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--accent-rose)' }}>
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                  </svg>
                  <Link to={`/documents/${doc.id}`} style={{ fontWeight: 600, color: 'var(--text-pure)', fontSize: '0.9rem' }}>
                    {doc.title}
                  </Link>
                </span>
                <div className="doc-actions-group">
                  {doc.url && (
                    <a href={doc.url} target="_blank" rel="noreferrer" className="action-pill action-pill-pdf" title="View Source PDF">PDF &nearr;</a>
                  )}
                  <Link to={`/documents/${doc.id}#tab-extracted-text`} className="action-pill action-pill-ocr">OCR</Link>
                  <a href={`/documents/${doc.id}/download/txt`} className="action-pill action-pill-txt">TXT &darr;</a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
