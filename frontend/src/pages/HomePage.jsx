import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Sparkles, Languages, ShieldCheck, Database, Layers, ArrowRight } from 'lucide-react';

export function HomePage() {
  const [stats, setStats] = useState({
    atoms_count: 24,
    documents_count: 815,
    pages_count: 4830,
    languages_count: 4,
  });
  const [atoms, setAtoms] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [aiQuery, setAiQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, atomsData] = await Promise.allSettled([
          api.getPlatformStats(),
          api.getAtoms(24),
        ]);

        if (statsData.status === 'fulfilled') {
          const val = statsData.value || {};
          const s = val.stats || val;
          setStats({
            atoms_count: s.atoms_count || 24,
            documents_count: s.documents_count ?? s.total_documents ?? 815,
            pages_count: s.pages_count ?? 4830,
            languages_count: 4,
          });
        }

        if (atomsData.status === 'fulfilled') {
          const a = atomsData.value;
          setAtoms(Array.isArray(a) ? a : a?.atoms || a?.items || []);
        }
      } catch (err) {
        console.error('HomePage data load error:', err);
      }
    }
    loadData();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
    }
  };

  const handleAiSubmit = (e) => {
    e.preventDefault();
    if (aiQuery.trim()) {
      navigate(`/ai-research?query=${encodeURIComponent(aiQuery.trim())}`);
    }
  };

  return (
    <>
      {/* Hero Section */}
      <section className="hero-section">
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1.25rem' }}>
          <span className="hero-brand-plain">CALIP</span>
        </div>
        <div className="hero-pill">
          <Sparkles size={14} />
          24 Canonical Pilot Atoms from longtailcases.com &bull; Cognitive Atomic Legal Intelligence Platform
        </div>
        <h1 className="hero-title">
          Cognitive Atomic Legal Intelligence Platform
        </h1>
        <p className="hero-subtitle">
          Dedicated exclusively to the 24 Pilot FIR Atoms. Seamless vernacular preservation (Marathi, Gujarati, Bengali, Hindi) alongside authoritative English legal translations, dynamic adaptive briefings, and 100% verifiable citations.
        </p>

        {/* Universal Search Bar */}
        <div className="search-container">
          <form onSubmit={handleSearchSubmit}>
            <div className="search-input-group">
              <input
                type="text"
                name="q"
                className="search-input"
                placeholder="Search the 24 Atoms by FIR number (147/2002), police station (Kotwali), statute (Sec 406 IPC), or party..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                required
              />
              <button type="submit" className="btn btn-primary">Search 24 Atoms</button>
            </div>
          </form>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '0.85rem', fontSize: '0.85rem', color: 'var(--text-dim)', flexWrap: 'wrap' }}>
            <span>Quick Inquiries:</span>
            <Link to="/atoms" style={{ color: 'var(--accent-cyan)', fontWeight: 600 }}>Explore All 24 Atoms</Link> &bull;
            <Link to="/ai-research?query=What+are+the+charges+and+acts+in+the+Nagpur+case+FIR+147+2002" style={{ color: 'var(--text-muted)' }}>Nagpur FIR 147/2002</Link> &bull;
            <Link to="/ai-research?query=Show+bilingual+Marathi+and+English+allegations+for+Maharashtra+cases" style={{ color: 'var(--text-muted)' }}>Bilingual Marathi / English</Link> &bull;
            <Link to="/documents" style={{ color: 'var(--text-muted)' }}>815 Evidence Documents</Link>
          </div>
        </div>
      </section>

      {/* Stats Grid: Centered on the 24 Pilot Atoms */}
      <section className="stats-grid">
        <div className="stat-card">
          <span className="stat-label">Canonical FIR Atoms</span>
          <span className="stat-number">{stats.atoms_count || 24}</span>
          <span style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)' }}>From longtailcases.com</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Multilingual Vernaculars</span>
          <span className="stat-number">4 States</span>
          <span style={{ fontSize: '0.8rem', color: 'var(--accent-emerald)' }}>मराठी, ગુજરાતી, বাংলা, हिंदी</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Evidentiary Documents</span>
          <span className="stat-number">{stats.documents_count}</span>
          <span style={{ fontSize: '0.8rem', color: 'var(--accent-amber)' }}>PDFs, Exhibits, Panchnamas</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Grounded Vector Chunks</span>
          <span className="stat-number">5,554</span>
          <span style={{ fontSize: '0.8rem', color: '#a5b4fc' }}>Atom-partitioned vector index</span>
        </div>
      </section>

      {/* AI Assistant Spotlight */}
      <section className="ai-box">
        <div className="ai-header">
          <div style={{ padding: '0.6rem', background: 'rgba(99, 102, 241, 0.2)', borderRadius: 'var(--radius-md)' }}>
            <Sparkles size={24} color="#818cf8" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--text-main)' }}>Dynamic AI Legal Reasoner</h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Adaptive legal briefings: generates comparative Markdown tables, timelines, and bilingual cards based on your inquiry.</p>
          </div>
        </div>

        <form onSubmit={handleAiSubmit} style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
          <input
            type="text"
            name="query"
            className="search-input"
            style={{
              background: 'rgba(255, 255, 255, 0.9)',
              border: '1px solid rgba(0, 0, 0, 0.08)',
              borderRadius: 'var(--radius-full)',
              padding: '0.8rem 1.4rem',
              color: 'var(--text-pure)',
              boxShadow: '0 4px 14px rgba(0, 0, 0, 0.03)',
            }}
            placeholder="e.g., Compare the accused, statutory charges, and alleged overt acts in the Nagpur case (FIR 147/2002) in a table..."
            value={aiQuery}
            onChange={(e) => setAiQuery(e.target.value)}
            required
          />
          <button type="submit" className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Sparkles size={16} />
            <span>Generate Briefing</span>
          </button>
        </form>
      </section>

      {/* 24 Canonical Pilot Atoms Showcase Table */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', marginTop: '2rem' }}>
        <div>
          <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: 'var(--text-main)', margin: 0 }}>
            The 24 Canonical Pilot Atoms
          </h2>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Extracted directly from longtailcases.com and hydrated across 25 analytical layers.
          </p>
        </div>
        <Link to="/atoms" className="btn btn-secondary btn-sm" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>View All 24 Dossiers</span>
          <ArrowRight size={14} />
        </Link>
      </div>

      <div className="category-block" style={{ marginBottom: '3.5rem' }}>
        <table className="detail-table">
          <thead>
            <tr style={{ background: 'rgba(255, 255, 255, 0.02)' }}>
              <th>Canonical FIR Identity</th>
              <th>Jurisdiction &amp; Police Station</th>
              <th>Original Language</th>
              <th>FIR Number / Year</th>
              <th>Statutory Sections</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {atoms.slice(0, 10).map((a) => (
              <tr key={a.id}>
                <td>
                  <Link to={`/atoms/${a.id}`} style={{ fontWeight: 700, color: 'var(--accent-cyan)', fontFamily: 'var(--font-mono)' }}>
                    {a.canonical_fir_id}
                  </Link>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                    {a.original_language_summary ? `${a.original_language_summary.slice(0, 60)}...` : a.summary ? `${a.summary.slice(0, 60)}...` : 'Canonical FIR record'}
                  </div>
                </td>
                <td>
                  <strong style={{ color: 'var(--text-pure)' }}>{a.police_station} PS</strong>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>{a.district}, {a.state}</div>
                </td>
                <td>
                  <span className="badge badge-indigo" style={{ fontSize: '0.75rem' }}>
                    {a.original_language || 'Marathi (मराठी)'}
                  </span>
                </td>
                <td>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: '#f1f5f9' }}>
                    {a.fir_number}/{a.fir_year}
                  </span>
                </td>
                <td>
                  <span className="badge badge-cyan" style={{ fontSize: '0.72rem' }}>
                    {a.sections || 'IPC'}
                  </span>
                </td>
                <td>
                  <Link to={`/atoms/${a.id}`} className="btn btn-secondary btn-sm" style={{ fontSize: '0.8rem' }}>
                    Inspect Dossier &rarr;
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
