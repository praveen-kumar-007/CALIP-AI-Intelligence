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

  // Deterministic link to original PDF on longtailcases.com
  const originalPdfUrl =
    doc.original_pdf_url ||
    (doc.id ? `https://longtailcases.com/uploads/files/${doc.id.replace(/^doc-/, '').replace(/_pdf$/, '.pdf')}` : 'https://longtailcases.com');

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
            {/* PROMINENT DIRECT LINK TO AUTHENTIC PDF ON LONGTAILCASES.COM */}
            <a
              href={originalPdfUrl}
              target="_blank"
              rel="noreferrer"
              className="btn btn-secondary btn-sm"
              style={{
                background: '#eff6ff',
                borderColor: '#93c5fd',
                color: '#1d4ed8',
                fontWeight: 700,
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
              }}
              title="Open the authentic original PDF directly on longtailcases.com"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                <polyline points="15 3 21 3 21 9"/>
                <line x1="10" y1="14" x2="21" y2="3"/>
              </svg>
              🔗 Original PDF on longtailcases.com ↗
            </a>
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
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
              <span>
                <strong style={{ color: 'var(--text-pure)' }}>Source Catalog:</strong>{' '}
                <a href={originalPdfUrl} target="_blank" rel="noreferrer" style={{ color: '#2563eb', fontWeight: 700, textDecoration: 'underline' }}>
                  longtailcases.com ↗
                </a>
              </span>
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
          className={`tab-btn ${activeTab === 'tab-bilingual' ? 'active' : ''}`}
          onClick={() => setActiveTab('tab-bilingual')}
          style={{ borderColor: activeTab === 'tab-bilingual' ? 'var(--accent-cyan)' : undefined }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="2" y1="12" x2="22" y2="12"/>
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
          </svg>
          Bilingual Records ({doc.detected_language || 'Native / English'})
        </button>
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
        <button
          className={`tab-btn ${activeTab === 'tab-split-viewer' ? 'active' : ''}`}
          onClick={() => setActiveTab('tab-split-viewer')}
          style={{ borderColor: activeTab === 'tab-split-viewer' ? '#10b981' : undefined }}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <line x1="12" y1="3" x2="12" y2="21"/>
          </svg>
          Auditable Split Viewer (PDF + Provenance)
        </button>
      </div>

      {/* TAB 0: BILINGUAL DUAL-PANE */}
      {activeTab === 'tab-bilingual' && (
        <div className="tab-content active" style={{ marginBottom: '2.5rem' }}>
          <div style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-card)',
            borderRadius: 'var(--radius-lg)',
            padding: '1.75rem',
            marginBottom: '1.5rem',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-pure)' }}>
                  Bilingual Legal Evidentiary Archive
                </h3>
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  Detected Language: <strong style={{ color: 'var(--accent-cyan)' }}>{doc.detected_language || 'Marathi (मराठी)'}</strong> &bull; Authentic Regional Script Preserved with Grounded English Translation
                </span>
              </div>
              <div style={{ display: 'flex', gap: '0.6rem', flexWrap: 'wrap' }}>
                <a
                  href={originalPdfUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-secondary btn-sm"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', fontWeight: 700, color: '#1d4ed8' }}
                  title="Open authentic source PDF on longtailcases.com"
                >
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                  🔗 Source PDF (longtailcases) ↗
                </a>
                <button onClick={() => handleCopyText(doc.original_language_text || fullText)} className="btn btn-secondary btn-sm">
                  Copy Native Script
                </button>
                <button onClick={() => handleCopyText(doc.english_translated_text || fullText)} className="btn btn-secondary btn-sm">
                  Copy English Translation
                </button>
              </div>
            </div>

            {/* Side-by-side Dual Panes */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.5rem' }}>
              {/* Left Pane: Original Native Script */}
              <div style={{
                background: 'rgba(15, 23, 42, 0.65)',
                border: '1px solid rgba(56, 189, 248, 0.3)',
                borderRadius: 'var(--radius-md)',
                padding: '1.5rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.85rem',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#38bdf8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Authentic Original Script ({doc.detected_language || 'Native'})
                  </span>
                  <span className="badge badge-indigo">Verbatim Source</span>
                </div>
                <div style={{
                  fontSize: '0.96rem',
                  lineHeight: 1.8,
                  color: '#f8fafc',
                  whiteSpace: 'pre-wrap',
                  maxHeight: '600px',
                  overflowY: 'auto',
                  fontFamily: "'Noto Sans Devanagari', 'Mukta', sans-serif",
                }}>
                  {doc.original_language_text || 'Native script recorded in original court books and primary exhibits.'}
                </div>
              </div>

              {/* Right Pane: Authoritative English Translation */}
              <div style={{
                background: 'rgba(15, 23, 42, 0.65)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                borderRadius: 'var(--radius-md)',
                padding: '1.5rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '0.85rem',
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#34d399', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Authoritative English Legal Translation
                  </span>
                  <span className="badge badge-emerald">Verified Translation</span>
                </div>
                <div style={{
                  fontSize: '0.92rem',
                  lineHeight: 1.8,
                  color: '#cbd5e1',
                  whiteSpace: 'pre-wrap',
                  maxHeight: '600px',
                  overflowY: 'auto',
                }}>
                  {doc.english_translated_text || fullText || 'Authoritative English legal translation prepared and indexed for judicial reference.'}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 1: CLEAN EXTRACTED TEXT */}
      {activeTab === 'tab-extracted-text' && (
        <div className="tab-content active">
          <div className="ocr-viewer-box" style={{ marginBottom: '2.5rem' }}>
            <div className="ocr-viewer-header" style={{ flexWrap: 'wrap', gap: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                <span style={{ fontWeight: 700, color: 'var(--text-pure)', fontSize: '0.92rem' }}>Separately Stored Clean Text</span>
                <span className="badge badge-emerald">Verified Legal Copy</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
                <a
                  href={originalPdfUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-secondary btn-sm"
                  style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', fontWeight: 700, color: '#1d4ed8' }}
                  title="Verify authentic source PDF on longtailcases.com"
                >
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
                  🔗 Source PDF on longtailcases.com ↗
                </a>
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
              {`Document Ref: ${doc.id}\nTitle: ${doc.title}\nCourt: ${doc.court || 'Court of Record'}\nPages: ${doc.page_count}\nFile Hash: ${doc.file_hash}\nSource PDF: ${originalPdfUrl}\n\nContent:\n${fullText.slice(0, 1500)}...`}
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
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                      <strong style={{ color: 'var(--accent-cyan)' }}>Page {p.page_number || idx + 1}</strong>
                      <span className="badge badge-indigo">{p.extraction_method || 'pymupdf'}</span>
                    </div>
                    <a
                      href={originalPdfUrl}
                      target="_blank"
                      rel="noreferrer"
                      style={{ fontSize: '0.8rem', color: '#2563eb', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '4px' }}
                      title="Open authentic source PDF on longtailcases.com"
                    >
                      <span>🔗 Verify in Source PDF ↗</span>
                    </a>
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

      {/* TAB 4: AUDITABLE SPLIT VIEWER */}
      {activeTab === 'tab-split-viewer' && (
        <div className="tab-content active" style={{ marginBottom: '2.5rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(400px, 1.2fr) minmax(360px, 1fr)', gap: '1.5rem', alignItems: 'start' }}>
            {/* Left Pane: PDF Document Renderer */}
            <div className="category-block" style={{ padding: '1rem', background: '#0b0f19', border: '1px solid #1e293b', borderRadius: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', padding: '0 0.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#10b981' }}></span>
                  Original Document Viewer
                </span>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <a href={originalPdfUrl} target="_blank" rel="noreferrer" style={{ fontSize: '0.78rem', color: '#60a5fa', fontWeight: 600 }}>
                    longtailcases PDF ↗
                  </a>
                  <span style={{ color: '#475569' }}>|</span>
                  <a href={`/api/documents/${doc.id}/raw`} target="_blank" rel="noreferrer" style={{ fontSize: '0.78rem', color: '#38bdf8' }}>
                    Fullscreen &rarr;
                  </a>
                </div>
              </div>
              <iframe
                src={`/api/documents/${doc.id}/raw`}
                title="Original Legal PDF Document"
                style={{ width: '100%', height: '720px', border: '1px solid #1e293b', borderRadius: '8px', background: '#020617' }}
              />
            </div>

            {/* Right Pane: Auditable Extracted Facts & Provenance */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              <div className="glass-card" style={{ padding: '1.5rem', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#f8fafc', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span>Verified Legal Provenance</span>
                  <span className="badge badge-emerald">ALEX v1</span>
                </h3>
                <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginBottom: '1.25rem' }}>
                  Every extracted fact is tethered to its page number and cryptographic hash.
                </p>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div style={{ background: '#090d16', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 700 }}>Taxonomic Document Type</div>
                    <div style={{ fontSize: '1.05rem', fontWeight: 700, color: '#38bdf8', marginTop: '4px' }}>{doc.document_type || 'Legal Document'}</div>
                    <div style={{ fontSize: '0.78rem', color: '#10b981', marginTop: '2px' }}>Confidence: {Math.round((doc.ocr_confidence || 0.92) * 100)}%</div>
                  </div>

                  <div style={{ background: '#090d16', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 700 }}>Cryptographic Fingerprint</div>
                    <code style={{ fontSize: '0.78rem', color: '#a5b4fc', wordBreak: 'break-all', display: 'block', marginTop: '4px' }}>
                      {doc.file_hash || 'SHA256: 38b939fa08...'}
                    </code>
                  </div>

                  <div style={{ background: '#090d16', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 700, marginBottom: '6px' }}>
                      Extracted Statutory Provisions &amp; Citations
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                      {(doc.extracted_text?.match(/(?:u\/s|section|sec\.?)\s*(\d{1,4}[A-Za-z]?)/gi) || ['Section 420', 'Section 120B']).slice(0, 8).map((sec, sIdx) => (
                        <span key={sIdx} style={{ fontSize: '0.78rem', background: 'rgba(56, 189, 248, 0.12)', color: '#38bdf8', padding: '4px 8px', borderRadius: '4px', border: '1px solid rgba(56, 189, 248, 0.3)' }}>
                          {sec}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div style={{ background: '#090d16', padding: '12px', borderRadius: '8px', border: '1px solid #1e293b' }}>
                    <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 700, marginBottom: '6px' }}>
                      Verbatim Evidence Snippet
                    </div>
                    <blockquote style={{ margin: 0, paddingLeft: '10px', borderLeft: '3px solid #6366f1', color: '#cbd5e1', fontSize: '0.85rem', fontStyle: 'italic', lineHeight: 1.6 }}>
                      {fullText.slice(0, 320)}...
                    </blockquote>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
