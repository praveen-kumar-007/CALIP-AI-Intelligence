import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';

export function LongtailPage() {
  const [catalog, setCatalog] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCatalog() {
      try {
        setLoading(true);
        const data = await api.getLongtailCatalog();
        setCatalog(data);
      } catch (err) {
        console.error('Failed loading catalog:', err);
      } finally {
        setLoading(false);
      }
    }
    loadCatalog();
  }, []);

  const handleHarvest = async (e) => {
    e.preventDefault();
    try {
      await api.harvestLongtail();
      alert('Full catalog harvest started in background!');
      const data = await api.getLongtailCatalog();
      setCatalog(data);
    } catch (err) {
      alert('Harvest trigger failed: ' + err.message);
    }
  };

  const categories = catalog?.categories || {};

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
            <Link to="/" style={{ color: 'var(--text-dim)', fontSize: '0.85rem' }}>Home</Link>
            <span style={{ color: 'var(--text-dim)' }}>&bull;</span>
            <span style={{ color: 'var(--accent-cyan)', fontSize: '0.85rem' }}>Longtail Hierarchy</span>
          </div>
          <h1 style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-main)' }}>Longtail Cases Hierarchical Catalog</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
            Direct hierarchical structure from longtailcases.com: Category &rarr; Case &rarr; Folder &rarr; Subfolder &rarr; Document PDF.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <form onSubmit={handleHarvest}>
            <button type="submit" className="btn btn-secondary btn-sm">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="23 4 23 10 17 10"/>
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
              </svg>
              Re-sync Upstream
            </button>
          </form>
          <a href="/api/longtail/catalog" target="_blank" rel="noreferrer" className="btn btn-primary btn-sm">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
            Export Tree JSON
          </a>
        </div>
      </div>

      <div className="tree-container">
        {Object.entries(categories).map(([catName, cases]) => (
          <div className="category-block" key={catName} id={catName.replace(/\s+/g, '_')}>
            <div className="category-header">
              <div className="category-title">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--accent-cyan)' }}>
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                </svg>
                <span>{catName}</span>
              </div>
              <span className="badge badge-indigo">{(cases || []).length} Case Records</span>
            </div>

            <div className="case-folder-list">
              {(cases || []).map((caseItem, idx) => (
                <div className="case-tree-node" key={idx}>
                  <div className="case-tree-header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <Link to={`/cases/${caseItem.case_id || caseItem.id}`} style={{ fontWeight: 700, color: 'var(--text-main)', fontSize: '1.05rem' }}>
                        {caseItem.title}
                      </Link>
                      {caseItem.case_number && caseItem.case_number !== 'MIS/SUMMARY' && (
                        <code style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: '#38bdf8', background: 'rgba(56, 189, 248, 0.1)', padding: '0.15rem 0.4rem', borderRadius: 4 }}>
                          {caseItem.case_number}
                        </code>
                      )}
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                      {caseItem.url && (
                        <a href={caseItem.url} target="_blank" rel="noreferrer" style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                          Source &nearr;
                        </a>
                      )}
                      <Link to={`/cases/${caseItem.case_id || caseItem.id}`} className="btn btn-secondary btn-sm" style={{ padding: '0.2rem 0.5rem', fontSize: '0.75rem' }}>
                        View Case
                      </Link>
                    </div>
                  </div>

                  {/* Direct Documents */}
                  {caseItem.documents && caseItem.documents.length > 0 && (
                    <div style={{ marginLeft: '0.5rem', marginBottom: '0.75rem' }}>
                      <div style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '0.4rem' }}>
                        Direct Documents ({caseItem.documents.length})
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem' }}>
                        {caseItem.documents.map((doc, dIdx) => (
                          <div className="doc-link-item" key={dIdx}>
                            <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--accent-rose)' }}>
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                                <polyline points="14 2 14 8 20 8"/>
                              </svg>
                              <Link to={`/documents/${doc.id || doc.doc_id}`} style={{ color: 'var(--text-main)', fontWeight: 500 }}>{doc.title}</Link>
                            </span>
                            <div style={{ display: 'flex', gap: '0.5rem' }}>
                              {doc.url && (
                                <a href={doc.url} target="_blank" rel="noreferrer" className="btn btn-outline-cyan btn-sm" style={{ padding: '0.15rem 0.45rem', fontSize: '0.75rem' }}>
                                  PDF &nearr;
                                </a>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Nested Folders */}
                  {caseItem.folders && caseItem.folders.length > 0 && (
                    <div className="folder-tree">
                      {caseItem.folders.map((folder, fIdx) => (
                        <div className="folder-item" key={fIdx}>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                            <span style={{ fontWeight: 600, color: '#a5b4fc', display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.9rem' }}>
                              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                              </svg>
                              {folder.title}
                            </span>
                            <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>
                              {(folder.documents || []).length} files
                            </span>
                          </div>

                          {folder.documents && folder.documents.length > 0 && (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', marginBottom: '0.65rem' }}>
                              {folder.documents.map((fdoc, fdIdx) => (
                                <div key={fdIdx} className="doc-link-item" style={{ padding: '0.4rem 0.65rem', background: 'rgba(255, 255, 255, 0.7)', borderRadius: 'var(--radius-xs)', border: '1px solid rgba(0,0,0,0.03)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.4rem' }}>
                                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem' }}>
                                    <span style={{ color: 'var(--text-dim)' }}>&bull;</span>
                                    <Link to={`/documents/${fdoc.doc_id || fdoc.id}`} style={{ color: 'var(--text-pure)', fontWeight: 500 }}>{fdoc.title}</Link>
                                  </span>
                                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                    {fdoc.has_txt && <span className="action-status-badge">&#10003; TXT Ready</span>}
                                    <div className="doc-actions-group">
                                      {fdoc.url && (
                                        <a href={fdoc.url} target="_blank" rel="noreferrer" className="action-pill action-pill-pdf" title="View Source PDF">PDF &nearr;</a>
                                      )}
                                      <Link to={`/documents/${fdoc.doc_id || fdoc.id}#tab-extracted-text`} className="action-pill action-pill-ocr">OCR</Link>
                                      <a href={`/documents/${fdoc.doc_id || fdoc.id}/download/txt`} className="action-pill action-pill-txt">TXT &darr;</a>
                                    </div>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
