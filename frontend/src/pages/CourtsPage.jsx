import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';

export function CourtsPage() {
  const [courts, setCourts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCourts() {
      try {
        setLoading(true);
        const data = await api.getCourts();
        setCourts(Array.isArray(data) ? data : data?.courts || []);
      } catch (err) {
        console.error('Failed loading courts:', err);
      } finally {
        setLoading(false);
      }
    }
    loadCourts();
  }, []);

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
            Courts &amp; Jurisdictions
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>
            Hierarchical judicial registry covering Apex, High Courts, Sessions, Magistrate, and Special Courts.
          </p>
        </div>
        <div style={{ fontSize: '0.9rem', color: 'var(--text-dim)' }}>
          Showing <strong style={{ color: 'var(--text-main)' }}>{courts.length}</strong> courts
        </div>
      </div>

      <div className="card-grid">
        {courts.map((court, idx) => (
          <div className="legal-card" key={idx}>
            <div className="card-header">
              <div>
                <span className="badge badge-indigo" style={{ marginBottom: '0.35rem' }}>
                  {court.court_type || 'Court'}
                </span>
                <h2 className="card-title">{court.name}</h2>
              </div>
              <span className="badge badge-cyan">{court.state || court.jurisdiction_state || 'National'}</span>
            </div>

            <div className="meta-row">
              <div className="meta-item">
                <span>Jurisdiction: <strong>{court.jurisdiction || court.name}</strong></span>
              </div>
            </div>

            <p className="card-summary">
              Authoritative court forum handling trial proceedings, appeals, and revision applications cataloged in the system.
            </p>

            <div className="card-footer">
              <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                {court.case_count ?? 'Active'} case records
              </span>
              <Link to={`/cases?q=${encodeURIComponent(court.name)}`} className="btn btn-secondary btn-sm">
                Filter Cases &rarr;
              </Link>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
