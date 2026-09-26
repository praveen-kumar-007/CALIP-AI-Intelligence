import React, { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import logoHorizontal from '../../assets/logo-horizontal.png';
import logoDefault from '../../assets/logo.png';

export function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setMobileMenuOpen((prev) => !prev);
  };

  const closeMenu = () => {
    setMobileMenuOpen(false);
  };

  return (
    <header className="navbar">
      <div className="nav-container">
        <div className="nav-brand-group">
          <Link to="/" className="brand-logo" title="CALIP - Cognitive Atomic Legal Intelligence Platform">
            <img
              src={logoHorizontal}
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = logoDefault;
              }}
              alt="CALIP - Cognitive Atomic Legal Intelligence Platform"
              className="brand-logo-img"
            />
          </Link>
          <div className="pulse-indicator" title="Auto-Sync Engine active & monitoring upstream longtailcases.com">
            <span className="pulse-dot"></span>
            <span className="pulse-text">Live Sync</span>
          </div>
        </div>

        <ul className="nav-links">
          <li className="nav-item">
            <NavLink to="/" end className={({ isActive }) => (isActive ? 'active' : '')}>
              Home
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/atoms" className={({ isActive }) => (isActive ? 'active' : '')} style={{ color: 'var(--accent-cyan)', fontWeight: 700 }}>
              Atoms (FIR)
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/cases" className={({ isActive }) => (isActive ? 'active' : '')}>
              Cases
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/longtail" className={({ isActive }) => (isActive ? 'active' : '')}>
              Hierarchy
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/judgments" className={({ isActive }) => (isActive ? 'active' : '')}>
              Judgments
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/orders" className={({ isActive }) => (isActive ? 'active' : '')}>
              Orders
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/documents" className={({ isActive }) => (isActive ? 'active' : '')}>
              Documents
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/courts" className={({ isActive }) => (isActive ? 'active' : '')}>
              Courts
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/search" className={({ isActive }) => (isActive ? 'active' : '')}>
              Search
            </NavLink>
          </li>
          <li className="nav-item">
            <a href="/llms.txt" target="_blank" rel="noreferrer" title="Open AI Crawl Specification for Claude, ChatGPT & LLM agents" style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>
              llms.txt
            </a>
          </li>
        </ul>

        <div className="nav-cta">
          <Link to="/ai-research" className="btn btn-primary btn-sm nav-btn-desktop">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>
            </svg>
            <span className="btn-text">AI Research</span>
          </Link>
          <Link to="/admin" className="btn btn-secondary btn-sm nav-btn-desktop" title="Pipeline & OCR Engine Operations">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
            <span className="btn-text">Pipeline</span>
          </Link>

          {/* Mobile Menu Toggle Button (Hamburger) */}
          <button
            id="mobile-menu-btn"
            className={`mobile-toggle-btn ${mobileMenuOpen ? 'active' : ''}`}
            aria-label="Toggle navigation menu"
            aria-expanded={mobileMenuOpen ? 'true' : 'false'}
            onClick={toggleMobileMenu}
          >
            <span className="hamburger-bar"></span>
            <span className="hamburger-bar"></span>
            <span className="hamburger-bar"></span>
          </button>
        </div>
      </div>

      {/* Mobile Slide-Down Drawer Navigation */}
      <div id="mobile-drawer" className={`mobile-drawer ${mobileMenuOpen ? 'open' : ''}`}>
        <div className="mobile-drawer-inner">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem', paddingBottom: '0.85rem', borderBottom: '1px solid rgba(0,0,0,0.06)' }}>
            <img src={logoHorizontal} alt="CALIP" style={{ height: '34px', width: 'auto' }} />
            <div className="pulse-indicator">
              <span className="pulse-dot"></span>
              <span className="pulse-text">Live Sync</span>
            </div>
          </div>
          <div className="mobile-nav-grid">
            <Link to="/" className="mobile-nav-link" onClick={closeMenu}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
              Home
            </Link>
            <Link to="/atoms" className="mobile-nav-link" style={{ color: 'var(--accent-cyan)', fontWeight: 700 }} onClick={closeMenu}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="4"/></svg>
              Legal Atoms (FIR)
            </Link>
            <Link to="/cases" className="mobile-nav-link" onClick={closeMenu}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/><path d="M6 6h10"/><path d="M6 10h10"/></svg>
              Cases
            </Link>
            <Link to="/longtail" className="mobile-nav-link" onClick={closeMenu}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
              Hierarchy Tree
            </Link>
            <Link to="/judgments" className="mobile-nav-link" onClick={closeMenu}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>
              Judgments
            </Link>
            <Link to="/orders" className="mobile-nav-link" onClick={closeMenu}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
              Orders
            </Link>
            <Link to="/documents" className="mobile-nav-link" onClick={closeMenu}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              Documents &amp; OCR
            </Link>
            <Link to="/courts" className="mobile-nav-link" onClick={closeMenu}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
              Courts
            </Link>
            <Link to="/search" className="mobile-nav-link" onClick={closeMenu}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              Search Engine
            </Link>
            <a href="/llms.txt" target="_blank" rel="noreferrer" className="mobile-nav-link" style={{ color: 'var(--accent-primary)', fontWeight: 700 }} onClick={closeMenu}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/></svg>
              🤖 llms.txt (AI Crawl)
            </a>
            <a href="/api/open/dump" target="_blank" rel="noreferrer" className="mobile-nav-link" onClick={closeMenu}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
              Open DB Dump (JSON)
            </a>
          </div>
          <div className="mobile-drawer-cta">
            <Link to="/ai-research" className="btn btn-primary" style={{ flex: 1, justifyContent: 'center' }} onClick={closeMenu}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/></svg>
              AI Research
            </Link>
            <Link to="/admin" className="btn btn-secondary" style={{ flex: 1, justifyContent: 'center' }} onClick={closeMenu}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>
              Pipeline
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}
