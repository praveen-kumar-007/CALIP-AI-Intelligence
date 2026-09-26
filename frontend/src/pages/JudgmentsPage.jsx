import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';

export function JudgmentsPage() {
  const [judgments, setJudgments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadJudgments() {
      try {
        setLoading(true);
        const data = await api.getJudgments('', 60);
        setJudgments(Array.isArray(data) ? data : data?.judgments || data?.items || []);
      } catch (err) {
        console.error('Error loading judgments:', err);
      } finally {
        setLoading(false);
      }
    }
    loadJudgments();
  }, []);

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
            Library of Judgements &amp; Precedents
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>
            Authoritative court judgments, legal findings, issues, and precedents from Apex and High Courts.
          </p>
        </div>
        <div style={{ fontSize: '0.9rem', color: 'var(--text-dim)' }}>
          Showing <strong style={{ color: 'var(--text-main)' }}>{judgments.length}</strong> judgments
        </div>
      </div>

      <div className="card-grid">
        {judgments.map((j) => (
          <div className="legal-card" key={j.id}>
            <div className="card-header">
              <div>
                <span className="badge badge-indigo" style={{ marginBottom: '0.35rem' }}>Judgment</span>
                <h2 className="card-title">
                  <Link to={`/documents/${j.id || j.document_id}`}>{j.title}</Link>
                </h2>
              </div>
              <span className="badge badge-emerald">{j.date || j.judgment_date || 'Decided'}</span>
            </div>

            <div className="meta-row">
              <div className="meta-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                </svg>
                <span>{j.court || 'High Court'}</span>
              </div>
              {j.bench && (
                <div className="meta-item">
                  <span>Bench: {j.bench}</span>
                </div>
              )}
            </div>

            <p className="card-summary">
              {j.summary || 'Official judicial decision resolving statutory questions, evidence review, and legal findings.'}
            </p>

            <div className="card-footer">
              <Link to={`/cases/${j.case_id}`} style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                View Case Docket
              </Link>
              <Link to={`/documents/${j.id || j.document_id}`} className="btn btn-secondary btn-sm">
                Read Judgment &rarr;
              </Link>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
