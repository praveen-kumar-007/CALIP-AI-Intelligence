import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { api } from '../services/api';

export function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const queryParam = searchParams.get('q') || '';

  const [queryInput, setQueryInput] = useState(queryParam);
  const [results, setResults] = useState([]);
  const [vectorResults, setVectorResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const executeSearch = async (q) => {
    if (!q.trim()) return;
    setLoading(true);
    try {
      const data = await api.searchLegal(q.trim());
      setResults(data.results || data.cases || []);
      setVectorResults(data.vector_results || data.chunks || []);
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (queryParam) {
      setQueryInput(queryParam);
      executeSearch(queryParam);
    }
  }, [queryParam]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (queryInput.trim()) {
      setSearchParams({ q: queryInput.trim() });
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
          Legal Hybrid Search
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>
          Full-text keyword matching combined with semantic vector retrieval across cases, documents, sections, and courts.
        </p>
      </div>

      <div className="search-container" style={{ marginBottom: '2.5rem' }}>
        <form onSubmit={handleSubmit}>
          <div className="search-input-group">
            <input
              type="text"
              name="q"
              value={queryInput}
              onChange={(e) => setQueryInput(e.target.value)}
              className="search-input"
              placeholder="Search by case number, title, section (e.g. 406 IPC), court..."
              required
            />
            <button type="submit" className="btn btn-primary">Search</button>
          </div>
        </form>
      </div>

      {queryParam && (
        <>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '8px' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-main)' }}>
              Results for <span style={{ color: 'var(--accent-cyan)' }}>&ldquo;{queryParam}&rdquo;</span>
            </h2>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-dim)' }}>
              {results.length} case match(es) &bull; {vectorResults.length} document chunk match(es)
            </span>
          </div>

          {/* Matching Cases */}
          {results.length > 0 && (
            <div style={{ marginBottom: '2.5rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#a5b4fc', textTransform: 'uppercase', marginBottom: '1rem' }}>
                Matched Cases ({results.length})
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {results.map((caseItem, idx) => (
                  <div key={idx} className="legal-card" style={{ padding: '1.25rem 1.5rem' }}>
                    <div className="card-header">
                      <div>
                        <span className="badge badge-indigo" style={{ marginBottom: '0.3rem' }}>
                          {caseItem.subject || 'Legal Case'}
                        </span>
                        <h4 style={{ fontSize: '1.15rem', fontWeight: 700 }}>
                          <Link to={`/cases/${caseItem.id}`}>{caseItem.title}</Link>
                        </h4>
                      </div>
                      <code style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: '#38bdf8' }}>
                        {caseItem.case_number}
                      </code>
                    </div>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>
                      {caseItem.summary || 'Official case record preserved in CALIP database.'}
                    </p>
                    <div className="card-footer">
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Court: {caseItem.court}</span>
                      <Link to={`/cases/${caseItem.id}`} className="btn btn-secondary btn-sm">Open Case &rarr;</Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Matching Vector Chunks */}
          {vectorResults.length > 0 && (
            <div style={{ marginBottom: '3rem' }}>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#67e8f9', textTransform: 'uppercase', marginBottom: '1rem' }}>
                Semantic Vector Evidence Chunks ({vectorResults.length})
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {vectorResults.map((chk, idx) => (
                  <div key={idx} className="citation-card" style={{ background: 'var(--bg-card)', borderLeft: '3px solid var(--accent-cyan)', padding: '1.25rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <strong style={{ color: 'var(--text-main)', fontSize: '1rem' }}>{chk.document_title || 'Document Record'}</strong>
                      <span className="badge badge-cyan">Page {chk.page_number || 1}</span>
                    </div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                      {chk.case_title && `Case: ${chk.case_title} • `}
                      Similarity: {chk.similarity_score ? Math.round(chk.similarity_score * 100) : 92}%
                    </div>
                    <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: 'var(--text-pure)', background: 'rgba(255, 255, 255, 0.9)', border: '1px solid rgba(0, 0, 0, 0.06)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
                      {chk.chunk_text || chk.snippet}
                    </div>
                    <div style={{ marginTop: '0.75rem', display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '0.5rem' }}>
                      <div className="doc-actions-group">
                        {chk.pdf_url && (
                          <a href={chk.pdf_url} target="_blank" rel="noreferrer" className="action-pill action-pill-pdf" title="View Source PDF">
                            PDF &nearr;
                          </a>
                        )}
                        <Link to={`/documents/${chk.document_id}#tab-extracted-text`} className="action-pill action-pill-ocr" title="Inspect OCR Text">
                          OCR
                        </Link>
                        <a href={`/documents/${chk.document_id}/download/txt`} className="action-pill action-pill-txt" title="Download Plain Extracted Text">
                          TXT &darr;
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {results.length === 0 && vectorResults.length === 0 && !loading && (
            <div className="category-block" style={{ padding: '3rem', textAlign: 'center' }}>
              <p style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>
                No legal cases or document chunks matched your query &ldquo;{queryParam}&rdquo;.
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
