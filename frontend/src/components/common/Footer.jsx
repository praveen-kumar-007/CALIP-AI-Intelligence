import React from 'react';
import { Link } from 'react-router-dom';
import logoHorizontal from '../../assets/logo-horizontal.png';
import logoDefault from '../../assets/logo.png';
import {
  Sparkles,
  Database,
  Layers,
  Search,
  ExternalLink,
  ShieldCheck,
  Cpu,
  FileCode,
  FolderTree,
  CheckCircle2,
  ArrowUpRight,
  Bot,
  Activity,
  FileText,
} from 'lucide-react';

export function Footer() {
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="footer-enhanced">
      {/* Decorative Gradient Accent Top Border */}
      <div className="footer-accent-bar" />

      <div className="footer-container-enhanced">
        {/* Top Section: Brand + Value Proposition + Live Sync Badge */}
        <div className="footer-top-grid">
          <div className="footer-brand-column">
            <Link to="/" className="footer-brand-link" onClick={scrollToTop}>
              <img
                src={logoHorizontal}
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = logoDefault;
                }}
                alt="CALIP - Cognitive Atomic Legal Intelligence Platform"
                className="footer-brand-logo"
              />
            </Link>
            <p className="footer-brand-desc">
              <strong>Cognitive Atomic Legal Intelligence Platform</strong> &mdash; A next-generation judicial
              research engine structuring 24 canonical FIR atoms, 818 evidentiary documents, and 41,248 sequenced
              pages from <em>longtailcases.com</em> with strict cryptographic provenance and zero hallucination.
            </p>

            <div className="footer-status-pill-group">
              <span className="footer-status-pill success">
                <span className="status-dot-pulse" />
                <span>Supabase Live</span>
              </span>
              <span className="footer-status-pill info">
                <Activity size={12} />
                <span>24 Pilot Atoms Active</span>
              </span>
              <span className="footer-status-pill purple">
                <Cpu size={12} />
                <span>Local Ollama AI</span>
              </span>
            </div>
          </div>

          {/* Quick Action Interactive Cards */}
          <div className="footer-quick-cards">
            <Link to="/ai-research" className="footer-quick-card primary" onClick={scrollToTop}>
              <div className="quick-card-icon">
                <Sparkles size={18} />
              </div>
              <div className="quick-card-text">
                <strong>AI Legal Reasoner</strong>
                <span>Dynamic comparative tables &amp; statutory briefs</span>
              </div>
              <ArrowUpRight size={16} className="quick-card-arrow" />
            </Link>

            <Link to="/database-hierarchy" className="footer-quick-card secondary" onClick={scrollToTop}>
              <div className="quick-card-icon">
                <FolderTree size={18} />
              </div>
              <div className="quick-card-text">
                <strong>DB &amp; Folder Hierarchy</strong>
                <span>1:1 mirror of longtailcases directory</span>
              </div>
              <ArrowUpRight size={16} className="quick-card-arrow" />
            </Link>
          </div>
        </div>

        {/* Middle Section: 4 Structured, Neatly Arranged Navigation Columns */}
        <div className="footer-nav-columns">
          {/* Column 1: Core Legal Intelligence */}
          <div className="footer-nav-col">
            <div className="footer-col-header">
              <Layers size={16} className="col-header-icon blue" />
              <span>Core Intelligence</span>
            </div>
            <ul className="footer-col-list">
              <li>
                <Link to="/atoms" onClick={scrollToTop}>
                  <span>24 Pilot Atoms (FIRs)</span>
                  <span className="footer-pill-tag">Core</span>
                </Link>
              </li>
              <li>
                <Link to="/ai-research" onClick={scrollToTop}>
                  <span>AI Legal Reasoner</span>
                  <span className="footer-pill-tag highlight">GPT/Qwen</span>
                </Link>
              </li>
              <li>
                <Link to="/documents" onClick={scrollToTop}>
                  <span>Documents &amp; Exhibits</span>
                  <span className="footer-pill-count">818</span>
                </Link>
              </li>
              <li>
                <Link to="/search" onClick={scrollToTop}>
                  <span>Unified Legal Search</span>
                </Link>
              </li>
              <li>
                <Link to="/admin/review-queue" onClick={scrollToTop}>
                  <span>Verification Queue</span>
                </Link>
              </li>
            </ul>
          </div>

          {/* Column 2: Longtailcases & Hierarchy */}
          <div className="footer-nav-col">
            <div className="footer-col-header">
              <FolderTree size={16} className="col-header-icon emerald" />
              <span>Hierarchy &amp; Catalog</span>
            </div>
            <ul className="footer-col-list">
              <li>
                <Link to="/database-hierarchy" onClick={scrollToTop}>
                  <span>1:1 Folder Hierarchy Explorer</span>
                  <span className="footer-pill-tag success">Live</span>
                </Link>
              </li>
              <li>
                <Link to="/database-hierarchy" onClick={scrollToTop}>
                  <span>Database Schemas (6 Models)</span>
                </Link>
              </li>
              <li>
                <Link to="/documents" onClick={scrollToTop}>
                  <span>Bilingual Records (मराठी/English)</span>
                </Link>
              </li>
              <li>
                <a href="https://longtailcases.com" target="_blank" rel="noreferrer">
                  <span>longtailcases.com Source</span>
                  <ExternalLink size={12} className="footer-ext-icon" />
                </a>
              </li>
              <li>
                <Link to="/admin" onClick={scrollToTop}>
                  <span>Pipeline &amp; Auto-Sync Engine</span>
                </Link>
              </li>
            </ul>
          </div>

          {/* Column 3: AI Agents & Open Standards */}
          <div className="footer-nav-col">
            <div className="footer-col-header">
              <Bot size={16} className="col-header-icon indigo" />
              <span>AI &amp; Developer APIs</span>
            </div>
            <ul className="footer-col-list">
              <li>
                <a href="/llms.txt" target="_blank" rel="noreferrer" className="llms-link">
                  <span>🤖 llms.txt (AI Crawl Spec)</span>
                  <span className="footer-pill-tag cyan">Standard</span>
                </a>
              </li>
              <li>
                <a href="/llms-full.txt" target="_blank" rel="noreferrer">
                  <span>Full Corpus Markdown (.md)</span>
                </a>
              </li>
              <li>
                <a href="/api/open/dump" target="_blank" rel="noreferrer">
                  <span>Open Database Dump (JSON)</span>
                </a>
              </li>
              <li>
                <a href="/docs" target="_blank" rel="noreferrer">
                  <span>OpenAPI Interactive Swagger</span>
                  <ExternalLink size={12} className="footer-ext-icon" />
                </a>
              </li>
              <li>
                <a href="/robots.txt" target="_blank" rel="noreferrer">
                  <span>robots.txt</span>
                </a>
                <span className="separator">&bull;</span>
                <a href="/sitemap.xml" target="_blank" rel="noreferrer">
                  <span>sitemap.xml</span>
                </a>
              </li>
            </ul>
          </div>

          {/* Column 4: Cryptography & Provenance */}
          <div className="footer-nav-col">
            <div className="footer-col-header">
              <ShieldCheck size={16} className="col-header-icon purple" />
              <span>Verifiable Provenance</span>
            </div>
            <div className="footer-provenance-box">
              <div className="provenance-item">
                <span className="prov-label">Cryptographic Digest:</span>
                <span className="prov-value">SHA-256 Per Document</span>
              </div>
              <div className="provenance-item">
                <span className="prov-label">Vector Store:</span>
                <span className="prov-value">pgvector 384-dim Dense</span>
              </div>
              <div className="provenance-item">
                <span className="prov-label">OCR Engines:</span>
                <span className="prov-value">PyMuPDF Text + Tesseract</span>
              </div>
              <div className="provenance-item">
                <span className="prov-label">Local Model:</span>
                <span className="prov-value">Ollama qwen3:8b (Offline)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Section: Copyright & Compliance */}
        <div className="footer-bottom-bar">
          <div className="footer-copyright">
            &copy; {new Date().getFullYear()} <strong>CALIP</strong> &mdash; Cognitive Atomic Legal Intelligence Platform.
            Built for rigorous Indian criminal jurisprudence &amp; trial court research.
          </div>

          <div className="footer-badges">
            <span className="footer-security-badge" title="All statements backed by cryptographic page-level citations">
              <CheckCircle2 size={13} style={{ color: '#10b981' }} />
              <span>100% Grounded Citations</span>
            </span>
            <span className="footer-security-badge" title="No ungrounded generative hallucinations">
              <ShieldCheck size={13} style={{ color: '#3b82f6' }} />
              <span>Deterministic Retrieval</span>
            </span>
            <button onClick={scrollToTop} className="footer-back-to-top" title="Scroll back to top of page">
              <span>Back to Top &uarr;</span>
            </button>
          </div>
        </div>
      </div>
    </footer>
  );
}
