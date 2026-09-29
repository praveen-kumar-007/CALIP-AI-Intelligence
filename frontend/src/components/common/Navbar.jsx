import React, { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';

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
          <Link to="/" className="brand-logo" title="CALIP">
            CALIP
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
              24 Pilot Atoms (FIR)
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/ai-research" className={({ isActive }) => (isActive ? 'active' : '')}>
              AI Legal Reasoner
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/documents" className={({ isActive }) => (isActive ? 'active' : '')}>
              Documents &amp; Exhibits
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/database-hierarchy" className={({ isActive }) => (isActive ? 'active' : '')} style={{ fontWeight: 600 }}>
              DB &amp; Folder Hierarchy
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/search" className={({ isActive }) => (isActive ? 'active' : '')}>
              Search
            </NavLink>
          </li>
          <li className="nav-item">
            <NavLink to="/admin/review-queue" className={({ isActive }) => (isActive ? 'active' : '')}>
              Verification Queue
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
            <Link to="/" className="brand-logo" onClick={closeMenu}>CALIP</Link>
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
              24 Pilot Atoms (FIR)
            </Link>
            <Link to="/ai-research" className="mobile-nav-link" onClick={closeMenu}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/></svg>
              AI Legal Reasoner
            </Link>
            <Link to="/documents" className="mobile-nav-link" onClick={closeMenu}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
              Documents &amp; Exhibits
            </Link>
            <Link to="/database-hierarchy" className="mobile-nav-link" onClick={closeMenu}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
              DB &amp; Folder Hierarchy
            </Link>
            <Link to="/search" className="mobile-nav-link" onClick={closeMenu}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              Unified Search
            </Link>
            <Link to="/admin/review-queue" className="mobile-nav-link" onClick={closeMenu}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
              Verification Queue
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
