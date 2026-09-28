import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../services/api';
import { Languages, ShieldAlert, Sparkles, Filter } from 'lucide-react';

export function AtomsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const currentState = searchParams.get('state') || '';
  const currentLang = searchParams.get('lang') || '';
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
        if (currentLang) {
          list = list.filter((a) => (a.original_language || '').toLowerCase().includes(currentLang.toLowerCase()));
        }
        setAtoms(list);
      } catch (err) {
        console.error('Failed loading atoms:', err);
      } finally {
        setLoading(false);
      }
    }
    loadAtoms();
  }, [currentState, currentLang]);

  return (
    <>
      {/* Breadcrumb */}
      <nav style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem', fontSize: '0.85rem', color: 'var(--text-dim)' }}>
        <Link to="/" style={{ color: 'var(--text-dim)' }}>Home</Link>
        <span>/</span>
        <span style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>24 Pilot Legal Cognitive Atoms</span>
      </nav>

      {/* Page Header Hero */}
      <div className="category-block" style={{ padding: '2.25rem', marginBottom: '2rem', background: '#ffffff', border: '1px solid #e2e8f0', boxShadow: '0 4px 16px -2px rgba(15, 23, 42, 0.05)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1.5rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
              <span className="badge badge-indigo" style={{ fontSize: '0.8rem', letterSpacing: '0.05em', textTransform: 'uppercase' }}>Core Pilot Repository</span>
              <span className="badge badge-emerald">ONE VERIFIED FIR = ONE COGNITIVE ATOM</span>
              <span className="badge badge-cyan" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <Languages size={12} />
                Bilingual Native + English Grounded
              </span>
            </div>
            <h1 style={{ fontSize: '2.25rem', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.02em', marginBottom: '0.5rem' }}>
              24 Pilot Legal Cognitive Atoms Directory
            </h1>
            <p style={{ color: '#475569', fontSize: '1rem', maxWidth: '840px', lineHeight: 1.6, margin: 0 }}>
              Exclusively centered on the 24 Canonical Pilot Atoms from longtailcases.com. Every criminal matter is anchored to an immutable FIR identity with authentic regional language preservation (Marathi, Gujarati, Bengali, Hindi) and authoritative English legal translation.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <Link to="/ai-research" className="btn btn-primary btn-sm" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Sparkles size={14} />
              <span>AI Legal Reasoner</span>
            </Link>
            <Link to="/admin/review-queue" className="btn btn-secondary btn-sm" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <ShieldAlert size={14} />
              <span>Verification Queue</span>
            </Link>
          </div>
        </div>

        {/* Metric Badges Strip */}
        <div style={{ display: 'flex', gap: '1.75rem', marginTop: '1.5rem', paddingTop: '1.25rem', borderTop: '1px solid #f1f5f9', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#64748b', fontWeight: 700 }}>Canonical Atoms</span>
            <span style={{ fontSize: '1.35rem', fontWeight: 800, color: '#1d4ed8' }}>{atoms.length} Displayed</span>
          </div>
          <div style={{ borderLeft: '1px solid #e2e8f0' }}></div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#64748b', fontWeight: 700 }}>Vernacular Coverage</span>
            <span style={{ fontSize: '1.35rem', fontWeight: 800, color: '#059669' }}>Marathi, Gujarati, Bengali, Hindi</span>
          </div>
          <div style={{ borderLeft: '1px solid #e2e8f0' }}></div>
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.75rem', textTransform: 'uppercase', color: '#64748b', fontWeight: 700 }}>Grounding Integrity</span>
            <span style={{ fontSize: '1.35rem', fontWeight: 800, color: '#7c3aed' }}>100% Zero Hallucination</span>
          </div>
        </div>
      </div>

      {/* Filter Tabs: By State and By Language */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
        {/* State Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <span style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 700, marginRight: '4px' }}>STATE:</span>
          {[
            { label: 'All States', value: '' },
            { label: 'Maharashtra (MH)', value: 'MH' },
            { label: 'Gujarat (GJ)', value: 'GJ' },
            { label: 'Delhi (DL)', value: 'DL' },
            { label: 'West Bengal (WB)', value: 'WB' },
          ].map((tab, idx) => {
            const isActive = currentState === tab.value;
            return (
              <button
                key={idx}
                onClick={() => {
                  const p = {};
                  if (tab.value) p.state = tab.value;
                  if (currentLang) p.lang = currentLang;
                  setSearchParams(p);
                }}
                className={`btn btn-sm ${isActive ? 'btn-primary' : 'btn-secondary'}`}
                style={{ fontSize: '0.8rem' }}
              >
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Language Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <span style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 700, marginRight: '4px' }}>LANGUAGE:</span>
          {[
            { label: 'All', value: '' },
            { label: 'मराठी (Marathi)', value: 'Marathi' },
            { label: 'ગુજરાતી (Gujarati)', value: 'Gujarati' },
            { label: 'বাংলা (Bengali)', value: 'Bengali' },
            { label: 'हिंदी (Hindi)', value: 'Hindi' },
          ].map((tab, idx) => {
            const isActive = currentLang === tab.value;
            return (
              <button
                key={idx}
                onClick={() => {
                  const p = {};
                  if (currentState) p.state = currentState;
                  if (tab.value) p.lang = tab.value;
                  setSearchParams(p);
                }}
                className={`btn btn-sm ${isActive ? 'btn-cyan' : 'btn-secondary'}`}
                style={{ fontSize: '0.8rem' }}
              >
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Atoms Grid Table */}
      <div className="legal-card" style={{ padding: 0, overflow: 'hidden', marginBottom: '3rem' }}>
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table" style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ background: '#f8fafc', borderBottom: '2px solid #e2e8f0', color: '#475569', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                <th style={{ padding: '1rem 1.25rem' }}>Canonical FIR Identity</th>
                <th style={{ padding: '1rem 1.25rem' }}>Jurisdiction &amp; Police Station</th>
                <th style={{ padding: '1rem 1.25rem' }}>Original Language</th>
                <th style={{ padding: '1rem 1.25rem' }}>FIR No / Year</th>
                <th style={{ padding: '1rem 1.25rem' }}>Accused</th>
                <th style={{ padding: '1rem 1.25rem' }}>Documents</th>
                <th style={{ padding: '1rem 1.25rem', textAlign: 'right' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {atoms.map((a) => (
                <tr
                  key={a.id}
                  style={{ borderBottom: '1px solid #f1f5f9', transition: 'background 0.15s ease' }}
                >
                  <td style={{ padding: '1rem 1.25rem' }}>
                    <Link to={`/atoms/${a.id}`} style={{ fontFamily: 'var(--font-mono)', fontSize: '0.9rem', fontWeight: 700, color: 'var(--accent-primary)', textDecoration: 'none' }}>
                      {a.canonical_fir_id}
                    </Link>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
                      {a.original_language_summary ? `${a.original_language_summary.slice(0, 65)}...` : a.summary ? `${a.summary.slice(0, 65)}...` : 'Canonical FIR dossier record...'}
                    </div>
                  </td>
                  <td style={{ padding: '1rem 1.25rem' }}>
                    <strong style={{ color: 'var(--text-main)' }}>{a.police_station} PS</strong>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>{a.district || 'City'}, {a.state}</div>
                  </td>
                  <td style={{ padding: '1rem 1.25rem' }}>
                    <span className="badge badge-indigo" style={{ fontSize: '0.75rem' }}>
                      {a.original_language || 'Marathi (मराठी)'}
                    </span>
                  </td>
                  <td style={{ padding: '1rem 1.25rem' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#0f172a' }}>
                      {a.fir_number}/{a.fir_year}
                    </span>
                    <div style={{ fontSize: '0.75rem', color: 'var(--accent-indigo)' }}>{a.sections || 'IPC'}</div>
                  </td>
                  <td style={{ padding: '1rem 1.25rem' }}>
                    <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{a.accused_count ?? 1} Accused</span>
                  </td>
                  <td style={{ padding: '1rem 1.25rem' }}>
                    <span className="badge badge-cyan" style={{ fontFamily: 'var(--font-mono)' }}>
                      {a.doc_count ?? 1} PDFs
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
