import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { api } from '../services/api';

export function AIResearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryParam = searchParams.get('query') || '';

  const [inputQuery, setInputQuery] = useState(queryParam);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);

  const executeResearch = async (q) => {
    if (!q.trim()) return;
    setLoading(true);
    try {
      const res = await api.askLegalAI(q.trim());
      setResult(res);
    } catch (err) {
      console.error('AI Research error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (queryParam) {
      setInputQuery(queryParam);
      executeResearch(queryParam);
    }
  }, [queryParam]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputQuery.trim()) {
      setSearchParams({ query: inputQuery.trim() });
    }
  };

  const copyBriefing = () => {
    if (!result?.answer) return;
    navigator.clipboard.writeText(result.answer);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
  };

  const samplePrompts = [
    { label: 'Nagpur Case (FIR 147/2002) Charges & Acts', query: 'What are the charges and acts in the Nagpur case (FIR 147/2002)?' },
    { label: 'Section 207 CrPC Rulings & Discovery', query: 'What did the court decide regarding Section 207 CrPC documents?' },
    { label: 'MIS Report Cases & FIR Hierarchy', query: 'What cases and FIR numbers are listed in the MIS report?' },
    { label: 'Section 409 IPC Ingredients & Precedents', query: 'What are the essential ingredients of Section 409 IPC criminal breach of trust?' },
  ];

  return (
    <div className="ai-research-container">
      {/* Hero Header */}
      <div className="ai-hero-header">
        <div className="hero-pill">
          <span className="pulsing-glow-dot"></span>
          Dual-Corpus Legal Intelligence &amp; Verified Research
        </div>
        <h1 className="ai-hero-title">
          AI Case Intelligence &amp; Verified Legal Citation Assistant
        </h1>
        <p className="ai-hero-subtitle">
          Cross-examines internal case records, FIR cognitive atoms, and verified Indian statutory provisions &amp; judicial authorities with pinpoint citations and structured legal matrices.
        </p>
      </div>

      {/* Apple Spotlight Glassmorphism Query Box */}
      <div className="ai-search-card">
        <form onSubmit={handleSubmit}>
          <div className="search-card-inner">
            <div className="search-textarea-wrapper">
              <textarea
                name="query"
                rows="3"
                className="ai-spotlight-textarea"
                placeholder="Ask any legal question (e.g. 'What are the charges and acts in the Nagpur case (FIR 147/2002)?', 'What did the court decide regarding Section 207 CrPC?')..."
                value={inputQuery}
                onChange={(e) => setInputQuery(e.target.value)}
                required
              />
            </div>

            <div className="search-action-bar">
              <div className="engine-meta-pill">
                <span className="engine-indicator"></span>
                <span>Engine: <strong style={{ color: 'var(--accent-primary)', fontFamily: 'var(--font-mono)' }}>OLLAMA (qwen3:8b)</strong></span>
                <span className="meta-separator">&bull;</span>
                <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>Dual Grounding Active</span>
              </div>
              <button type="submit" className="btn btn-primary btn-apple-action" disabled={loading}>
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="5 3 19 12 5 21 5 3"/>
                </svg>
                {loading ? 'Synthesizing...' : 'Generate Verified Briefing'}
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Quick Apple Prompt Capsule Chips */}
      <div className="suggested-queries-section">
        <div className="suggested-label">Suggested Legal Inquiries:</div>
        <div className="suggested-chips-grid">
          {samplePrompts.map((p, idx) => (
            <button
              key={idx}
              type="button"
              className="ios-prompt-pill"
              onClick={() => {
                setInputQuery(p.query);
                setSearchParams({ query: p.query });
              }}
              style={{ textAlign: 'left', cursor: 'pointer' }}
            >
              <span className="pill-sparkle">✨</span>
              <span>{p.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Pure Apple iOS Glassmorphism Briefing Display */}
      {result && (
        <div className="briefing-card" id="briefing-card">
          {/* Top Action Bar */}
          <div className="briefing-header-bar">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
              <span className="badge badge-emerald" style={{ padding: '0.35rem 0.85rem', fontSize: '0.82rem', fontWeight: 700, borderRadius: 'var(--radius-full)' }}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginRight: 4, display: 'inline-block', verticalAlign: -1 }}>
                  <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
                Official Legal Briefing
              </span>
              {result.sources && (
                <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  <strong style={{ color: 'var(--accent-cyan)' }}>{result.sources.length}</strong> CALIP Evidence Records
                </span>
              )}
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <button id="copy-briefing-btn" className="btn btn-secondary btn-sm" onClick={copyBriefing} title="Copy briefing text to clipboard">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
                {copySuccess ? 'Copied!' : 'Copy Briefing'}
              </button>
              <button className="btn btn-secondary btn-sm" onClick={() => window.print()} title="Print or Save as PDF">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="6 9 6 2 18 2 18 9"></polyline>
                  <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
                  <rect x="6" y="14" width="12" height="8"></rect>
                </svg>
                Print / PDF
              </button>
            </div>
          </div>

          {/* Structured Legal Briefing Output */}
          <div id="briefing-content" className="legal-briefing-body" style={{ whiteSpace: 'pre-wrap', lineHeight: 1.8 }}>
            {result.rendered_html ? (
              <div dangerouslySetInnerHTML={{ __html: result.rendered_html }} />
            ) : (
              result.answer || 'No briefing returned.'
            )}
          </div>

          {/* Evidentiary Citations Panel */}
          {result.sources && result.sources.length > 0 && (
            <div id="calip-citations-section" className="citations-section-box">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
                <h3 className="citation-group-title" style={{ color: 'var(--text-pure)' }}>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0284c7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                  </svg>
                  CALIP Internal Evidence Records &amp; Page Citations
                </h3>
                <span className="badge badge-cyan">{result.sources.length} Sources Grounded</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {result.sources.map((src, i) => (
                  <div key={i} style={{ background: '#ffffff', padding: '0.85rem 1.15rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                      <strong style={{ color: 'var(--accent-primary)', fontSize: '0.9rem' }}>
                        [{i + 1}] {typeof src === 'string' ? src : src.title || src.court || 'Court Exhibit'}
                      </strong>
                      {src.page && <span className="badge badge-indigo">Page {src.page}</span>}
                    </div>
                    {src.text && <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>{src.text}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
