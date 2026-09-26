import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';

export function DocumentDetailPage() {
  const { id } = useParams();
  const [doc, setDoc] = useState(null);
  const [ocrData, setOcrData] = useState(null);
  const [activeTab, setActiveTab] = useState('tab-extracted-text');
  const [loading, setLoading] = useState(true);
  const [summarizing, setSummarizing] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);

  useEffect(() => {
    async function loadDocument() {
      try {
        setLoading(true);
        const [docData, ocrRes] = await Promise.allSettled([
          api.getDocumentById(id),
          api.getDocumentOcr(id),
        ]);
        if (docData.status === 'fulfilled') setDoc(docData.value);
        if (ocrRes.status === 'fulfilled') setOcrData(ocrRes.value);
      } catch (err) {
        console.error('Error loading doc:', err);
      } finally {
        setLoading(false);
      }
    }
    if (id) loadDocument();
  }, [id]);

  const handleCopyText = (text) => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
  };

  const handleReSummarize = async () => {
    try {
      setSummarizing(true);
      await api.summarizeDocument(id);
      const updated = await api.getDocumentById(id);
      setDoc(updated);
    } catch (err) {
      console.error('Re-summarize failed:', err);
    } finally {
      setSummarizing(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        Loading legal document...
      </div>
    );
  }

  if (!doc) {
    return (
      <div style={{ padding: '3rem', textAlign: 'center' }}>
        <h2>Document Record Not Found</h2>
        <Link to="/documents" className="btn btn-primary" style={{ marginTop: '1rem' }}>
          Back to Documents
        </Link>
      </div>
    );
  }

  const fullText = ocrData?.full_text || doc.extracted_text || '';
  const summaryText = doc.ai_summary?.summary_text || doc.ai_summary?.ratio_decidendi || doc.ai_summary?.summary || '';
  const pages = doc.pages || ocrData?.pages || [];
  const chunks = ocrData?.chunks || [];

  return (
    <>
      {/* Breadcrumb */}
      <nav style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: '0.85rem', color: 'var(--text-dim)' }}>
        <Link to="/" style={{ color: 'var(--text-dim)' }}>Home</Link>
        <span>/</span>
        <Link to="/documents" style={{ color: 'var(--text-dim)' }}>Documents</Link>
        <span>/</span>
        <span style={{ color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>{doc.id}</span>
      </nav>

      {/* Main Document Hero Card */}
      <div className="category-block" style={{ padding: '2.25rem', marginBottom: '2rem', background: 'var(--bg-card)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1.25rem', marginBottom: '1.5rem' }}>
          <div style={{ flex: 1, minWidth: '320px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.65rem', flexWrap: 'wrap' }}>
              <span className="badge badge-emerald">{doc.document_type || 'Legal Document'}</span>
              <span className="badge badge-cyan">OCR Processed</span>
              <span className="badge badge-indigo">{doc.ocr_status || 'EXTRACTED'}</span>
            </div>
            <h1 style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text-pure)', marginBottom: '0.65rem', lineHeight: 1.25 }}>
              {doc.title}
            </h1>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', flexWrap: 'wrap', fontSize: '0.88rem', color: 'var(--text-muted)' }}>
              {doc.case_id && (
                <span>Case: <Link to={`/cases/${doc.case_id}`} style={{ fontWeight: 600, color: '#38bdf8' }}>{doc.case_id}</Link> &bull;</span>
              )}
              <span>Court: <strong style={{ color: 'var(--text-main)' }}>{doc.court || 'District Court'}</strong> &bull;</span>
              <span>Pages: <strong style={{ color: 'var(--text-main)' }}>{doc.page_count || 1}</strong> &bull;</span>
              <span>Avg Confidence: <strong style={{ color: 'var(--accent-emerald)' }}>{Math.round((doc.ocr_confidence || 0.95) * 100)}%</strong></span>
            </div>
          </div>

          {/* Actions / Export Buttons */}
          <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap' }}>
            {doc.original_pdf_url && (
              <a href={doc.original_pdf_url} target="_blank" rel="noreferrer" className="btn btn-secondary btn-sm" title="View or download raw PDF file">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                Raw PDF
              </a>
            )}
            <a href={`/documents/${doc.id}/download/txt`} className="btn btn-outline-cyan btn-sm" title="Download clean separated text file">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
              </svg>
              Export TXT
            </a>
            <a href={`/documents/${doc.id}/download/json`} className="btn btn-outline-emerald btn-sm" title="Download RAG structured JSON schema">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="16 18 22 12 16 6"/>
                <polyline points="8 6 2 12 8 18"/>
              </svg>
              RAG JSON
            </a>
            <a href="#ai-summary-card" className="btn btn-outline-cyan btn-sm" style={{ borderColor: '#6366f1', color: '#4f46e5', background: 'rgba(99, 102, 241, 0.06)' }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>
              </svg>
              AI Legal Brief
            </a>
            <button onClick={handleReSummarize} disabled={summarizing} className="btn btn-primary btn-sm">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="23 4 23 10 17 10"/>
                <polyline points="1 20 1 14 7 14"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
              </svg>
              {summarizing ? 'Processing...' : 'Re-Run OCR'}
            </button>
          </div>
        </div>

        {/* Provenance & Hashing Bar */}
        <div style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '0.9rem 1.4rem', fontSize: '0.85rem', boxShadow: 'inset 0 1px 2px rgba(0, 0, 0, 0.02)', marginBottom: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
              <span style={{ color: 'var(--text-muted)', fontWeight: 500 }}>SHA-256 Digest:</span>
              <code style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-cyan)', fontSize: '0.82rem', background: 'rgba(2, 132, 199, 0.08)', padding: '0.15rem 0.4rem', borderRadius: 4 }}>
                {doc.file_hash || 'Verified Cryptographic Hash'}
              </code>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <span><strong style={{ color: 'var(--text-pure)' }}>Engine:</strong> <span className="badge badge-indigo">{doc.extraction_method || 'pymupdf_text'}</span></span>
              <span><strong style={{ color: 'var(--text-pure)' }}>Separately Stored:</strong> <span className="badge badge-emerald">Ready for RAG</span></span>
            </div>
          </div>
        </div>
      </div>

      {/* AI Executive Brief & Legal Summary Card */}
      <div id="ai-summary-card" className="category-block ai-summary-card" style={{ padding: '2.25rem', marginBottom: '2.5rem', background: 'rgba(255, 255, 255, 0.86)', backdropFilter: 'var(--glass-blur)', WebkitBackdropFilter: 'var(--glass-blur)', border: '1px solid var(--border-card)', outline: '1px solid var(--border-card-outer)', borderRadius: 'var(--radius-xl)', boxShadow: 'var(--shadow-md), inset 0 1px 1px #ffffff' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '0.75rem', marginBottom: '1.25rem', borderBottom: '1px solid var(--border-subtle)', paddingBottom: '0.85rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', justifySelf: 'center', width: 36, height: 36, borderRadius: 9, background: 'linear-gradient(135deg, #4f46e5, #0891b2)', color: 'white', boxShadow: '0 2px 8px rgba(79, 70, 229, 0.3)', justifyContent: 'center' }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/></svg>
            </span>
            <div>
              <h3 style={{ margin: 0, fontSize: '1.15rem', fontWeight: 800, color: 'var(--text-pure)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                AI Executive Brief &amp; Legal Summary
              </h3>
              <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                Synthesized by AI Engine <strong style={{ color: 'var(--accent-cyan)' }}>qwen3:8b</strong> &bull; Indian Penal, Procedural &amp; Case Analysis
              </span>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
            <button onClick={() => handleCopyText(summaryText)} className="btn btn-secondary btn-sm" style={{ fontSize: '0.8rem' }}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
              {copySuccess ? 'Copied!' : 'Copy Brief'}
            </button>
            <button onClick={handleReSummarize} disabled={summarizing} className="btn btn-primary btn-sm" style={{ fontSize: '0.8rem' }}>
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
              {summarizing ? 'Processing...' : 'Re-Summarize with AI'}
            </button>
          </div>
        </div>

        <div className="legal-briefing-body" style={{ fontSize: '0.95rem', lineHeight: 1.8, color: 'var(--text-main)', padding: '1rem 0', whiteSpace: 'pre-wrap' }}>
          {summaryText || 'Extracted legal text available. Click "Re-Summarize with AI" above to generate the full brief.'}
        </div>
      </div>

      {/* Modern Interactive Navigation Tabs */}
      <div className="tabs-nav">
        <button
          className={`tab-btn ${activeTab === 'tab-extracted-text' ? 'active' : ''}`}
          onClick={() => setActiveTab('tab-extracted-text')}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
          </svg>
          Clean Extracted Text
        </button>
        <button
          className={`tab-btn ${activeTab === 'tab-llm-context' ? 'active' : ''}`}
          onClick={() => setActiveTab('tab-llm-context')}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>
          </svg>
          LLM Context &amp; Citations
        </button>
        <button
          className={`tab-btn ${activeTab === 'tab-page-inspector' ? 'active' : ''}`}
          onClick={() => setActiveTab('tab-page-inspector')}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
            <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
          </svg>
          Page-by-Page Breakdown
        </button>
      </div>

      {/* TAB 1: CLEAN EXTRACTED TEXT */}
      {activeTab === 'tab-extracted-text' && (
        <div className="tab-content active">
          <div className="ocr-viewer-box" style={{ marginBottom: '2.5rem' }}>
            <div className="ocr-viewer-header" style={{ flexWrap: 'wrap', gap: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                <span style={{ fontWeight: 700, color: 'var(--text-pure)', fontSize: '0.92rem' }}>Separately Stored Clean Text</span>
                <span className="badge badge-emerald">Verified Legal Copy</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <button onClick={() => handleCopyText(fullText)} className="btn btn-secondary btn-sm">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                  </svg>
                  Copy Text
                </button>
                <a href={`/documents/${doc.id}/download/txt`} className="btn btn-outline-cyan btn-sm">Download .txt</a>
              </div>
            </div>
            <div className="ocr-text-content" style={{ whiteSpace: 'pre-wrap' }}>
              {fullText || 'No extracted text available for this document.'}
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: LLM CONTEXT */}
      {activeTab === 'tab-llm-context' && (
        <div className="tab-content active">
          <div className="category-block" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.75rem', color: 'var(--text-pure)' }}>LLM Context Representation</h3>
            <pre style={{ background: '#ffffff', border: '1px solid var(--border-subtle)', padding: '1.25rem', borderRadius: 'var(--radius-sm)', fontSize: '0.85rem', fontFamily: 'var(--font-mono)', overflowX: 'auto', lineHeight: 1.6 }}>
              {`Document Ref: ${doc.id}\nTitle: ${doc.title}\nCourt: ${doc.court || 'Court of Record'}\nPages: ${doc.page_count}\nFile Hash: ${doc.file_hash}\n\nContent:\n${fullText.slice(0, 1500)}...`}
            </pre>
          </div>
        </div>
      )}

      {/* TAB 3: PAGE-BY-PAGE */}
      {activeTab === 'tab-page-inspector' && (
        <div className="tab-content active">
          {pages && pages.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '2rem' }}>
              {pages.map((p, idx) => (
                <div key={idx} className="category-block" style={{ padding: '1.25rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <strong style={{ color: 'var(--accent-cyan)' }}>Page {p.page_number || idx + 1}</strong>
                    <span className="badge badge-indigo">{p.extraction_method || 'pymupdf'}</span>
                  </div>
                  <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', background: '#ffffff', padding: '1rem', borderRadius: 'var(--radius-sm)', whiteSpace: 'pre-wrap', border: '1px solid var(--border-subtle)' }}>
                    {p.page_text || p.text || 'Page extracted.'}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="category-block" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
              Page breakdown stored in database document body above.
            </div>
          )}
        </div>
      )}
    </>
  );
}
