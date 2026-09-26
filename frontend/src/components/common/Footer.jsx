import React from 'react';
import { Link } from 'react-router-dom';
import calipLogo from '../../assets/logo.png';
import logoHorizontal from '../../assets/logo-horizontal.png';

export function Footer() {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '2rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.65rem' }}>
              <img
                src={calipLogo}
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = logoHorizontal;
                }}
                alt="CALIP - Cognitive Atomic Legal Intelligence Platform"
                style={{ height: '52px', width: 'auto', objectFit: 'contain' }}
              />
            </div>
            <p style={{ maxWidth: '500px', color: 'var(--text-dim)', fontSize: '0.85rem', lineHeight: '1.6' }}>
              <strong>Cognitive Atomic Legal Intelligence Platform</strong> &mdash; Source-grounded legal research platform structuring cases, judgments, orders, applications, and documents from longtailcases.com with cryptographic provenance and page-level citations.
            </p>
          </div>
          <div className="footer-links">
            <Link to="/cases">Cases Index</Link>
            <Link to="/longtail">Longtail Tree</Link>
            <Link to="/judgments">Judgments</Link>
            <Link to="/orders">Orders</Link>
            <Link to="/documents">Documents</Link>
            <Link to="/courts">Courts</Link>
            <Link to="/acts">Acts &amp; Sections</Link>
            <Link to="/ai-research">AI Assistant</Link>
            <a href="/llms.txt" target="_blank" rel="noreferrer" style={{ color: 'var(--accent-primary)', fontWeight: 600 }}>🤖 llms.txt (AI Crawl)</a>
            <a href="/llms-full.txt" target="_blank" rel="noreferrer">Full Corpus (.md)</a>
            <a href="/api/open/dump" target="_blank" rel="noreferrer">Open DB Dump (JSON)</a>
            <a href="/api" target="_blank" rel="noreferrer">API Specs</a>
            <a href="/robots.txt" target="_blank" rel="noreferrer">robots.txt</a>
            <a href="/sitemap.xml" target="_blank" rel="noreferrer">sitemap.xml</a>
            <Link to="/about">About &amp; Provenance</Link>
          </div>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid var(--border-subtle)', paddingTop: '1.25rem', fontSize: '0.8rem', marginTop: '1.5rem', flexWrap: 'wrap', gap: '8px' }}>
          <span>Legal Information &amp; Case Intelligence Platform &bull; Strictly grounded in verified documents.</span>
          <span>Hardware: NVIDIA RTX 3050 &bull; Local Ollama active</span>
        </div>
      </div>
    </footer>
  );
}
