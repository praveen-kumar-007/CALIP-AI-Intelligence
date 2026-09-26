import React from 'react';
import { Link } from 'react-router-dom';
import { Layers, ShieldAlert, Users, Calendar, Sparkles, CheckCircle2 } from 'lucide-react';
import { StatusBadge } from '../common/StatusBadge';

export function AtomCard({ atom }) {
  if (!atom) return null;

  const confidencePercent = atom.confidence_score ? Math.round(atom.confidence_score * 100) : 95;
  const isHydrated = atom.hydration_status === 'HYDRATED' || atom.is_verified;

  return (
    <div className="glass-card glass-card-interactive" style={{ display: 'flex', flexDirection: 'column', gap: '14px', position: 'relative', overflow: 'hidden' }}>
      {/* Top accent glow line */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '3px',
        background: isHydrated ? 'linear-gradient(90deg, #10b981, #06b6d4)' : 'linear-gradient(90deg, #6366f1, #a855f7)',
      }} />

      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '10px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Layers size={16} color="#06b6d4" />
            <span style={{
              fontSize: '0.75rem',
              fontFamily: 'var(--font-mono)',
              color: '#67e8f9',
              fontWeight: 600,
            }}>
              CANONICAL FIR ATOM
            </span>
          </div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 800, color: '#f8fafc', marginTop: '6px' }}>
            <Link to={`/atoms/${encodeURIComponent(atom.id || atom.canonical_fir_id)}`} style={{ color: 'inherit' }}>
              {atom.canonical_fir_id || `ATOM-${atom.id}`}
            </Link>
          </h3>
        </div>
        <StatusBadge status={atom.hydration_status || 'HYDRATED'} />
      </div>

      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', fontSize: '0.8rem', color: '#94a3b8' }}>
        <span><strong>Station:</strong> {atom.police_station || 'Central Jurisdiction'}</span>
        <span>&bull;</span>
        <span><strong>Year:</strong> {atom.fir_year || '2023'}</span>
        <span>&bull;</span>
        <span><strong>State:</strong> {atom.state || 'Delhi'}</span>
      </div>

      {/* Sections / Offenses */}
      {atom.charges_sections && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <ShieldAlert size={14} color="#f43f5e" />
          <span style={{ fontSize: '0.78rem', color: '#fca5a5', fontWeight: 600 }}>Sections:</span>
          {Array.isArray(atom.charges_sections) ? (
            atom.charges_sections.map((sec, idx) => (
              <span key={idx} style={{
                background: 'rgba(244, 63, 94, 0.1)',
                border: '1px solid rgba(244, 63, 94, 0.25)',
                color: '#fda4af',
                fontSize: '0.72rem',
                padding: '1px 6px',
                borderRadius: '4px',
                fontFamily: 'var(--font-mono)',
              }}>
                {sec}
              </span>
            ))
          ) : (
            <span style={{ fontSize: '0.75rem', color: '#cbd5e1' }}>{atom.charges_sections}</span>
          )}
        </div>
      )}

      {/* Hydration / Confidence Bar */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: '4px' }}>
          <span style={{ color: '#64748b' }}>Atomic Hydration Completeness</span>
          <span style={{ color: isHydrated ? '#6ee7b7' : '#a5b4fc', fontWeight: 700 }}>{confidencePercent}%</span>
        </div>
        <div style={{ height: '6px', background: '#1e293b', borderRadius: '3px', overflow: 'hidden' }}>
          <div style={{
            height: '100%',
            width: `${confidencePercent}%`,
            background: isHydrated ? 'linear-gradient(90deg, #10b981, #06b6d4)' : 'linear-gradient(90deg, #6366f1, #a855f7)',
            borderRadius: '3px',
          }} />
        </div>
      </div>

      {/* Action footer */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingTop: '12px',
        borderTop: '1px solid rgba(255, 255, 255, 0.06)',
        marginTop: 'auto',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.78rem', color: '#64748b' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Users size={13} /> {atom.accused_count ?? 1} Accused
          </span>
          <span>&bull;</span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Calendar size={13} /> {atom.proceedings_count ?? 2} Hearings
          </span>
        </div>

        <Link
          to={`/atoms/${encodeURIComponent(atom.id || atom.canonical_fir_id)}`}
          className="btn btn-secondary btn-sm"
          style={{ gap: '6px', color: '#67e8f9' }}
        >
          <Sparkles size={13} />
          <span>IRAC Reason</span>
        </Link>
      </div>
    </div>
  );
}
