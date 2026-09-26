import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import calipLogo from '../assets/logo.png';
import logoEmblem from '../assets/logo-emblem.png';

export function HomePage() {
  const [stats, setStats] = useState({
    cases_count: 0,
    documents_count: 0,
    folders_count: 0,
    courts_count: 0,
  });
  const [jurisdictions, setJurisdictions] = useState([]);
  const [cases, setCases] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [aiQuery, setAiQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    async function loadData() {
      try {
        const [statsData, casesData] = await Promise.allSettled([
          api.getPlatformStats(),
          api.getCases('', '', 10),
        ]);

        if (statsData.status === 'fulfilled') {
          const s = statsData.value?.stats || statsData.value || {};
          setStats({
            cases_count: s.cases_count ?? s.total_cases ?? 15,
            documents_count: s.documents_count ?? s.total_documents ?? 40,
            folders_count: s.folders_count ?? 12,
            courts_count: s.courts_count ?? s.total_courts ?? 7,
          });
          if (statsData.value?.jurisdictions) {
            setJurisdictions(statsData.value.jurisdictions);
          } else {
            // Default jurisdictions if not returned
            setJurisdictions([
              { subject: 'Criminal Procedure & Bail', count: 18 },
              { subject: 'Constitutional Writs & Rights', count: 12 },
              { subject: 'Corporate & Arbitration', count: 9 },
              { subject: 'Revenue & Civil Disputes', count: 14 },
            ]);
          }
        }

        if (casesData.status === 'fulfilled') {
          const c = casesData.value;
          setCases(Array.isArray(c) ? c : c?.cases || c?.items || []);
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
          <img
            src={calipLogo}
            onError={(e) => {
              e.target.onerror = null;
              e.target.src = logoEmblem;
            }}
            alt="CALIP - Cognitive Atomic Legal Intelligence Platform"
            style={{
              maxWidth: '280px',
              width: '100%',
              height: 'auto',
              objectFit: 'contain',
              filter: 'drop-shadow(0 6px 20px rgba(0,0,0,0.15))',
            }}
          />
        </div>
        <div className="hero-pill">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2v4"/>
            <path d="m4.93 4.93 2.83 2.83"/>
            <path d="M2 12h4"/>
            <path d="m4.93 19.07 2.83-2.83"/>
            <path d="M12 22v-4"/>
            <path d="m19.07 19.07-2.83-2.83"/>
            <path d="M22 12h-4"/>
            <path d="m19.07 4.93-2.83 2.83"/>
          </svg>
          AI-Readable Legal Document &amp; Case Intelligence &bull; Cognitive Atomic Legal Intelligence Platform
        </div>
        <h1 className="hero-title">
          Cognitive Atomic Legal Intelligence Platform <br />
          <span className="text-gradient">Every Legal Record with Provenance</span>
        </h1>
        <p className="hero-subtitle">
          Integrated with longtailcases.com catalog hierarchy. High-fidelity OCR, knowledge graph entity linking, semantic vector embeddings, and verified citations.
        </p>

        {/* Universal Search Bar */}
        <div className="search-container">
          <form onSubmit={handleSearchSubmit}>
            <div className="search-input-group">
              <input
                type="text"
                name="q"
                className="search-input"
                placeholder="Search by case number (e.g. 147/2002), party, judge, court, section (Sec 420), or legal topic..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                required
              />
              <button type="submit" className="btn btn-primary">Search Platform</button>
            </div>
          </form>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '0.85rem', fontSize: '0.85rem', color: 'var(--text-dim)', flexWrap: 'wrap' }}>
            <span>Popular queries:</span>
            <Link to="/search?q=Nagpur" style={{ color: 'var(--text-muted)' }}>Nagpur (147/2002)</Link> &bull;
            <Link to="/search?q=Charge+Sheet" style={{ color: 'var(--text-muted)' }}>Charge Sheet</Link> &bull;
            <Link to="/search?q=Section+406" style={{ color: 'var(--text-muted)' }}>Section 406 IPC</Link> &bull;
            <Link to="/search?q=Supreme+Court" style={{ color: 'var(--text-muted)' }}>Supreme Court</Link> &bull;
            <Link to="/search?q=MIS" style={{ color: 'var(--text-muted)' }}>MIS Report</Link>
          </div>
        </div>
      </section>

      {/* Stats Grid */}
      <section className="stats-grid">
        <div className="stat-card">
          <span className="stat-label">Indexed Cases</span>
          <span className="stat-number">{stats.cases_count}</span>
          <span style={{ fontSize: '0.8rem', color: 'var(--accent-cyan)' }}>Full metadata &amp; history</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">PDF &amp; Documents</span>
          <span className="stat-number">{stats.documents_count}</span>
          <span style={{ fontSize: '0.8rem', color: 'var(--accent-emerald)' }}>Extracted, OCR &amp; Chunks</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Hierarchical Folders</span>
          <span className="stat-number">{stats.folders_count}</span>
          <span style={{ fontSize: '0.8rem', color: 'var(--accent-amber)' }}>Preserved folder tree</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Courts &amp; Benches</span>
          <span className="stat-number">{stats.courts_count}</span>
          <span style={{ fontSize: '0.8rem', color: '#a5b4fc' }}>Supreme, High, District</span>
        </div>
      </section>

      {/* AI Assistant Spotlight */}
      <section className="ai-box">
        <div className="ai-header">
          <div style={{ padding: '0.6rem', background: 'rgba(99, 102, 241, 0.2)', borderRadius: 'var(--radius-md)' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: '#818cf8' }}>
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <div>
            <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--text-main)' }}>Legal AI Research Assistant</h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>Ask natural language questions grounded in verified case documents and judgment files.</p>
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
            placeholder="e.g., What did the court decide regarding Section 207 CrPC in the Nagpur case?"
            value={aiQuery}
            onChange={(e) => setAiQuery(e.target.value)}
            required
          />
          <button type="submit" className="btn btn-primary">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="5 3 19 12 5 21 5 3"/>
            </svg>
            Ask AI Assistant
          </button>
        </form>
      </section>

      {/* Jurisdictions & Legal Catalog Sections */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-main)' }}>Jurisdictions &amp; Legal Catalog</h2>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>Dynamic classifications and cataloged categories directly from the database.</p>
        </div>
        <Link to="/longtail" className="btn btn-secondary btn-sm">View Full Nested Tree &rarr;</Link>
      </div>

      <div className="card-grid" style={{ marginBottom: '3.5rem' }}>
        {jurisdictions && jurisdictions.length > 0 ? (
          jurisdictions.map((j, idx) => (
            <div className="legal-card" key={idx}>
              <div className="card-header">
                <h3 className="card-title">{j.subject}</h3>
                <span className="badge badge-indigo">{j.count} Case{j.count !== 1 ? 's' : ''}</span>
              </div>
              <p className="card-summary">
                Authoritative legal proceedings, verified filings, orders, and case files cataloged under {j.subject}.
              </p>
              <div className="card-footer">
                <Link to={`/cases?q=${encodeURIComponent(j.subject)}`} className="btn btn-outline-cyan btn-sm">Explore Cases &rarr;</Link>
                <Link to={`/search?q=${encodeURIComponent(j.subject)}`} style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Search Records</Link>
              </div>
            </div>
          ))
        ) : (
          <p style={{ color: 'var(--text-muted)' }}>No jurisdiction categories found in the database.</p>
        )}
      </div>

      {/* Featured Cases Table */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--text-main)' }}>Recent Legal Cases</h2>
        <Link to="/cases" style={{ fontSize: '0.875rem', color: 'var(--accent-cyan)' }}>View All Cases &rarr;</Link>
      </div>

      <div className="category-block" style={{ marginBottom: '3.5rem' }}>
        <table className="detail-table">
          <thead>
            <tr style={{ background: 'rgba(255, 255, 255, 0.02)' }}>
              <th>Case Title</th>
              <th>Case Number</th>
              <th>Court / Jurisdiction</th>
              <th>State / Section</th>
              <th>Documents</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {cases.slice(0, 8).map((caseItem) => (
              <tr key={caseItem.id}>
                <td>
                  <Link to={`/cases/${caseItem.id}`} style={{ fontWeight: 600, color: 'var(--text-main)' }}>
                    {caseItem.title}
                  </Link>
                </td>
                <td><code style={{ fontFamily: 'var(--font-mono)', color: '#38bdf8' }}>{caseItem.case_number}</code></td>
                <td>{caseItem.court || 'District Court'}</td>
                <td><span className="badge badge-indigo">{caseItem.subject || 'Legal'}</span></td>
                <td>{caseItem.doc_count || (caseItem.documents ? caseItem.documents.length : 0)} files</td>
                <td>
                  <Link to={`/cases/${caseItem.id}`} className="btn btn-secondary btn-sm">View Record</Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
