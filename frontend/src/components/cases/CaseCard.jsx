import React from 'react';
import { Link } from 'react-router-dom';

export function CaseCard({ caseItem }) {
  if (!caseItem) return null;

  return (
    <div className="legal-card">
      <div className="card-header">
        <div>
          <span className="badge badge-indigo" style={{ marginBottom: '0.4rem' }}>
            {caseItem.subject || 'Legal Case'}
          </span>
          <h2 className="card-title">
            <Link to={`/cases/${caseItem.id}`}>{caseItem.title}</Link>
          </h2>
        </div>
        <span className="badge badge-cyan" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem' }}>
          {caseItem.case_number || `CASE-${caseItem.id}`}
        </span>
      </div>

      <div className="meta-row">
        <div className="meta-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          </svg>
          <span>{caseItem.court || 'District Court'}</span>
        </div>
        <div className="meta-item">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          <span>Year {caseItem.case_year || '2002-2024'}</span>
        </div>
      </div>

      <p className="card-summary">
        {caseItem.summary || 'Official legal docket recording trial proceedings, interim and final orders, police charges, exhibits, and judgments.'}
      </p>

      <div className="card-footer">
        <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
          {caseItem.doc_count || (caseItem.documents ? caseItem.documents.length : 0)} attached documents
        </span>
        <Link to={`/cases/${caseItem.id}`} className="btn btn-secondary btn-sm">
          Explore Case &rarr;
        </Link>
      </div>
    </div>
  );
}
