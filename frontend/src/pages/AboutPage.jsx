import React from 'react';
import { Scale, Layers, ShieldCheck, Sparkles, Database, FileCode, CheckCircle2 } from 'lucide-react';

export function AboutPage() {
  return (
    <div className="container" style={{ maxWidth: '960px' }}>
      <div style={{ textAlign: 'center', marginBottom: '40px' }}>
        <div style={{
          width: '56px',
          height: '56px',
          borderRadius: '16px',
          background: 'linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 16px',
          boxShadow: '0 0 25px rgba(99, 102, 241, 0.4)',
        }}>
          <Scale size={28} color="#ffffff" />
        </div>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 800, color: '#f8fafc', marginBottom: '8px' }}>
          About CALIP Architecture
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '1rem', maxWidth: '640px', margin: '0 auto' }}>
          Cognitive Atomic Legal Intelligence Platform for Indian Jurisprudence.
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
        {/* Core Mission */}
        <div className="glass-card">
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#f8fafc', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Layers size={20} color="#818cf8" />
            <span>The Fragmented Indian Court Problem</span>
          </h2>
          <p style={{ color: '#cbd5e1', lineHeight: 1.8, fontSize: '0.94rem' }}>
            In Indian jurisprudence, a single dispute can generate dozens of separate court filings across different benches: an initial FIR at a local police station, a remand order before a Magistrate, anticipatory bail before the Sessions Court, a Section 482 petition in the High Court, and a Special Leave Petition in the Supreme Court.
            Each court assigns its own case number, making longitudinal tracking difficult.
          </p>
          <p style={{ color: '#cbd5e1', lineHeight: 1.8, fontSize: '0.94rem', marginTop: '12px' }}>
            <strong>CALIP introduces the Canonical Legal Cognitive Atom:</strong> a 25-layer schema that grounds all subsequent filings back to the originating Police Station & FIR Atom, assembling the entire procedural history into an unbroken timeline.
          </p>
        </div>

        {/* 25-Layer Breakdown */}
        <div className="glass-card">
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#f8fafc', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sparkles size={20} color="#06b6d4" />
            <span>25-Layer Atomic Intelligence Spec</span>
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '16px' }}>
            {[
              { title: '1. Inception Layer', desc: 'Police Station, FIR Number, Year, Distict, Cognizance' },
              { title: '2. Offenses & Penal Provisions', desc: 'IPC, BNS, CrPC sections, bailability, compounding' },
              { title: '3. Accused Entities', desc: 'Identities, aliases, custody status, bail history' },
              { title: '4. Procedural Chronology', desc: 'Charge sheet, committal, framing of charges, evidence' },
              { title: '5. Appellate Trajectory', desc: 'Writ petitions, appeals, SLPs across High Courts & SC' },
              { title: '6. Cryptographic Provenance', desc: 'SHA-256 PDF hashes, extracted page offsets, OCR confidence' },
            ].map((layer, idx) => (
              <div key={idx} style={{ background: '#111827', padding: '14px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
                <strong style={{ color: '#67e8f9', fontSize: '0.88rem', display: 'block', marginBottom: '4px' }}>{layer.title}</strong>
                <span style={{ color: '#94a3b8', fontSize: '0.82rem' }}>{layer.desc}</span>
              </div>
            ))}
          </div>
        </div>

        {/* AI & Open Data Access */}
        <div className="glass-card">
          <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#f8fafc', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <FileCode size={20} color="#10b981" />
            <span>AI-First Open Data Architecture</span>
          </h2>
          <p style={{ color: '#cbd5e1', lineHeight: 1.8, fontSize: '0.94rem' }}>
            CALIP is built with native machine endpoints so external AI assistants (ChatGPT, Claude, autonomous legal agents) can directly consume the knowledge base without authentication friction:
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginTop: '14px', fontFamily: 'var(--font-mono)', fontSize: '0.85rem' }}>
            <div style={{ background: '#090d16', padding: '10px 14px', borderRadius: '6px', color: '#a5b4fc' }}>
              GET /llms.txt &mdash; Curated documentation manifest for LLMs
            </div>
            <div style={{ background: '#090d16', padding: '10px 14px', borderRadius: '6px', color: '#67e8f9' }}>
              GET /llms-full.txt &mdash; Full database corpus rendered in structured Markdown
            </div>
            <div style={{ background: '#090d16', padding: '10px 14px', borderRadius: '6px', color: '#6ee7b7' }}>
              GET /api/open/dump &mdash; Unrestricted single-call database dump (JSON)
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
