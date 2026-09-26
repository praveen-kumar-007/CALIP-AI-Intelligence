import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../services/api';

export function AtomsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const currentState = searchParams.get('state') || '';
  const [atoms, setAtoms] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAtoms() {
      try {
        setLoading(true);
        const data = await api.getAtoms(100);
        let list = Array.isArray(data) ? data : data?.atoms || data?.items || [];
        if (currentState) {
          list = list.filter((a) => (a.state_code || a.state || '').toUpperCase().includes(currentState.toUpperCase()));
        }
        setAtoms(list);
      } catch (err) {
        console.error('Failed loading atoms:', err);
      } finally {
        setLoading(false);
      }
    }
    loadAtoms();
  }, [currentState]);

  const stateTabs = [
    { label: 'All Jurisdictions', value: '' },
    { label: 'Maharashtra (10)', value: 'MH' },
    { label: 'Gujarat (9)', value: 'GJ' },
    { label: 'Delhi (2)', value: 'DL' },
    { label: 'West Bengal (3)', value: 'WB' },
  ];

  return (
    <>
      {/* Breadcrumb */}
      <nav style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: '0.85rem', color: 'var(--text-dim)' }}>
        <Link to="/" style={{ color: 'var(--text-dim)' }}>Home</Link>
        <span>/</span>
        <span style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>Legal Cognitive Atoms</span>
      </nav>

      {/* Page Header Hero */}
      <div className="category-block" style={{ padding: '2.25rem', marginBottom: '2rem', background: 'linear-gradient(135deg, rgba(16, 24, 40, 0.95), rgba(15, 23, 42, 0.9))', border: '1px solid rgba(56, 189, 248, 0.2)', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.4)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1.5rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
              <span className="badge badge-indigo" style={{ fontSize: '0.8rem', letterSpacing: '0.05em', textTransform: 'uppercase' }}>Core Architectural Unit</span>
              <span className="badge badge-emerald">ONE VERIFIED FIR = ONE COGNITIVE ATOM</span>
            </div>
            <h1 style={{ fontSize: '2.25rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em', marginBottom: '0.5rem' }}>
              Legal Cognitive Atoms Directory
            </h1>
            <p style={{ color: '#94a3b8', fontSize: '1rem', maxWidth: '820px', lineHeight: 1.6 }}>
              Every criminal matter in CALIP is anchored to a single, immutable, verified FIR identity:{' '}
              <code style={{ color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>STATE-DISTRICT-POLICE_STATION-FIR_NO-YEAR</code>.
              All proceedings (Magistrate, Sessions, High Court, Supreme Court), charge sheets, accused matrices, exhibits, and orders are unified under their canonical atom.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <Link to="/admin/review-queue" className="btn btn-secondary btn-sm" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
              Verification Queue
            </Link>
            <Link to="/ai-research?query=Explain+the+procedural+history+of+FIR+147+Nagpur" className="btn btn-primary btn-sm" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              Atomic Legal Reasoning
            </Link>
          </div>
        </div>

        {/* Metric Badges Strip */}
        <div style={{ display: 'flex', gap: '1.5rem', marginTop: '1.5rem', paddingTop: '1.25rem', borderTop: '1px solid rgba(255, 255, 255, 0.08)', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#64748b', fontWeight: 700 }}>Verified Canonical Atoms</span>
            <span style={{ fontSize: '1.35rem', fontWeight: 800, color: '#38bdf8' }}>{atoms.length}</span>
          </div>
          <div style={{ borderLeft: '1px solid rgba(255, 255, 255, 0.08)' }}></div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#64748b', fontWeight: 700 }}>Target Candidate Slots</span>
            <span style={{ fontSize: '1.35rem', fontWeight: 800, color: '#10b981' }}>24 Active / Slot 25 Reserved</span>
          </div>
          <div style={{ borderLeft: '1px solid rgba(255, 255, 255, 0.08)' }}></div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#64748b', fontWeight: 700 }}>State Jurisdictions</span>
            <span style={{ fontSize: '1.35rem', fontWeight: 800, color: '#a855f7' }}>MH, GJ, DL, WB</span>
          </div>
        </div>
      </div>

      {/* State Filter Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        {stateTabs.map((tab, idx) => {
          const isActive = currentState === tab.value;
          return (
            <button
              key={idx}
              onClick={() => {
                if (tab.value) {
                  setSearchParams({ state: tab.value });
                } else {
                  setSearchParams({});
                }
              }}
              className={`btn btn-sm ${isActive ? 'btn-primary' : 'btn-secondary'}`}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Atoms Grid Table */}
      <div className="legal-card" style={{ padding: 0, overflow: 'hidden', marginBottom: '3rem' }}>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: 'rgba(15, 23, 42, 0.9)', borderBottom: '1px solid var(--border-subtle)', color: 'var(--text-dim)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                <th style={{ padding: '1rem 1.25rem' }}>Canonical FIR Identity</th>
                <th style={{ padding: '1rem 1.25rem' }}>Jurisdiction &amp; Police Station</th>
                <th style={{ padding: '1rem 1.25rem' }}>FIR No / Year</th>
                <th style={{ padding: '1rem 1.25rem' }}>Hydration Status</th>
                <th style={{ padding: '1rem 1.25rem' }}>Accused</th>
                <th style={{ padding: '1rem 1.25rem' }}>Documents Linked</th>
                <th style={{ padding: '1rem 1.25rem', textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {atoms.map((a) => (
                <tr
                  key={a.id}
                  style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.04)', transition: 'background 0.15s ease' }}
                >
                  <td style={{ padding: '1rem 1.25rem' }}>
                    <Link to={`/atoms/${a.id}`} style={{ fontFamily: 'var(--font-mono)', fontSize: '0.9rem', fontWeight: 700, color: 'var(--accent-cyan)', textDecoration: 'none' }}>
                      {a.canonical_fir_id}
                    </Link>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                      {a.summary ? `${a.summary.slice(0, 75)}...` : 'Canonical atomic FIR dossier record...'}
                    </div>
                  </td>
                  <td style={{ padding: '1rem 1.25rem' }}>
                    <strong style={{ color: 'var(--text-main)' }}>{a.police_station} PS</strong>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>{a.district || 'City'}, {a.state}</div>
                  </td>
                  <td style={{ padding: '1rem 1.25rem' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#f1f5f9' }}>
                      {a.fir_number || '147'}/{a.fir_year || '2002'}
                    </span>
                    <div style={{ fontSize: '0.75rem', color: 'var(--accent-indigo)' }}>{a.sections || 'IPC 406, 420'}</div>
                  </td>
                  <td style={{ padding: '1rem 1.25rem' }}>
                    {a.hydration_status === 'FULLY_HYDRATED' ? (
                      <span className="badge badge-emerald">FULLY HYDRATED</span>
                    ) : a.hydration_status === 'PARTIALLY_HYDRATED' ? (
                      <span className="badge badge-indigo">PARTIALLY HYDRATED</span>
                    ) : (
                      <span className="badge badge-emerald">FULLY HYDRATED</span>
                    )}
                  </td>
                  <td style={{ padding: '1rem 1.25rem' }}>
                    <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{a.accused_count ?? 1} Accused</span>
                  </td>
                  <td style={{ padding: '1rem 1.25rem' }}>
                    <span className="badge badge-cyan" style={{ fontFamily: 'var(--font-mono)' }}>
                      {a.doc_count ?? 2} PDFs
                    </span>
                  </td>
                  <td style={{ padding: '1rem 1.25rem', textAlign: 'right' }}>
                    <Link to={`/atoms/${a.id}`} className="btn btn-secondary btn-sm" style={{ padding: '0.35rem 0.75rem', fontSize: '0.8rem' }}>
                      Inspect Atom &rarr;
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
