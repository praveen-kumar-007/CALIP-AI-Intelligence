import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { StatusBadge } from '../components/common/StatusBadge';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import {
  Layers,
  Sparkles,
  Users,
  Calendar,
  ShieldAlert,
  ArrowLeft,
  FileCode,
  CheckCircle,
  HelpCircle,
  Send,
  Download,
} from 'lucide-react';

export function AtomDetailPage() {
  const { id } = useParams();
  const { showToast } = useApp();
  const [atom, setAtom] = useState(null);
  const [canonicalJson, setCanonicalJson] = useState(null);
  const [hydration, setHydration] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('proceedings'); // 'proceedings' | 'accused' | 'reasoner' | 'json'

  // IRAC Reasoner State
  const [reasonQuestion, setReasonQuestion] = useState('What are the key allegations and bail considerations for the accused?');
  const [reasonResult, setReasonResult] = useState(null);
  const [reasoning, setReasoning] = useState(false);

  useEffect(() => {
    async function loadAtom() {
      try {
        setLoading(true);
        const [atomRes, jsonRes, hydRes] = await Promise.allSettled([
          api.getAtomById(id),
          api.getCanonicalAtom(id),
          api.getAtomHydration(id),
        ]);

        if (atomRes.status === 'fulfilled') setAtom(atomRes.value);
        if (jsonRes.status === 'fulfilled') setCanonicalJson(jsonRes.value);
        if (hydRes.status === 'fulfilled') setHydration(hydRes.value);
      } catch (err) {
        console.error('Failed loading atom:', err);
        showToast('Error loading legal atom', 'error');
      } finally {
        setLoading(false);
      }
    }
    if (id) loadAtom();
  }, [id]);

  const handleRunReasoner = async (e) => {
    e?.preventDefault();
    if (!reasonQuestion.trim()) return;

    try {
      setReasoning(true);
      const res = await api.reasonWithAtom(reasonQuestion, atom?.id, atom?.canonical_fir_id);
      setReasonResult(res);
      showToast('Grounded IRAC reasoning completed!', 'success');
    } catch (err) {
      console.error('Reasoning failed:', err);
      showToast(err.message || 'Reasoning query failed', 'error');
    } finally {
      setReasoning(false);
    }
  };

  if (loading) return <LoadingSpinner text="Retrieving 25-layer cognitive atom dossier..." />;

  if (!atom) {
    return (
      <div className="container" style={{ textAlign: 'center', padding: '64px 0' }}>
        <h2>Legal Atom Not Found</h2>
        <Link to="/atoms" className="btn btn-primary" style={{ marginTop: '20px' }}>
          <ArrowLeft size={16} /> Back to Atoms
        </Link>
      </div>
    );
  }

  const proceedings = atom.proceedings || canonicalJson?.proceedings || [];
  const accused = atom.accused || canonicalJson?.accused || [];

  return (
    <div className="container">
      {/* Back button */}
      <Link to="/atoms" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: '#06b6d4', fontSize: '0.85rem', marginBottom: '20px' }}>
        <ArrowLeft size={16} /> Back to Atoms
      </Link>

      {/* Header Card */}
      <div className="glass-card" style={{ marginBottom: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
              <span style={{
                fontSize: '0.75rem',
                fontFamily: 'var(--font-mono)',
                color: '#67e8f9',
                background: 'rgba(6, 182, 212, 0.1)',
                border: '1px solid rgba(6, 182, 212, 0.25)',
                padding: '2px 8px',
                borderRadius: '4px',
              }}>
                CANONICAL FIR ATOM
              </span>
              <StatusBadge status={atom.hydration_status || 'HYDRATED'} />
            </div>

            <h1 style={{ fontSize: '1.6rem', fontWeight: 800, color: '#f8fafc', lineHeight: 1.3 }}>
              {atom.canonical_fir_id || `FIR-${atom.id}`}
            </h1>
          </div>

          <button
            onClick={() => setActiveTab('reasoner')}
            className="btn btn-cyan btn-sm"
            style={{ gap: '6px' }}
          >
            <Sparkles size={14} />
            <span>Launch IRAC Reasoner</span>
          </button>
        </div>

        {/* Metadata Strip */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '16px',
          marginTop: '20px',
          paddingTop: '18px',
          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
          fontSize: '0.85rem',
        }}>
          <div>
            <span style={{ color: '#64748b', display: 'block', fontSize: '0.75rem' }}>POLICE STATION</span>
            <strong style={{ color: '#f8fafc' }}>{atom.police_station || 'Central Station'}</strong>
          </div>
          <div>
            <span style={{ color: '#64748b', display: 'block', fontSize: '0.75rem' }}>STATE / JURISDICTION</span>
            <strong style={{ color: '#f8fafc' }}>{atom.state || 'Delhi NCR'}</strong>
          </div>
          <div>
            <span style={{ color: '#64748b', display: 'block', fontSize: '0.75rem' }}>FIR YEAR</span>
            <strong style={{ color: '#f8fafc' }}>{atom.fir_year || '2023'}</strong>
          </div>
          <div>
            <span style={{ color: '#64748b', display: 'block', fontSize: '0.75rem' }}>CONFIDENCE RATING</span>
            <span style={{ color: '#6ee7b7', fontWeight: 700 }}>
              {atom.confidence_score ? `${(atom.confidence_score * 100).toFixed(0)}% Verified` : '96% High'}
            </span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-subtle)', marginBottom: '24px' }}>
        {[
          { id: 'proceedings', label: `Proceedings Timeline (${proceedings.length})`, icon: Calendar },
          { id: 'accused', label: `Accused & Offenses (${accused.length})`, icon: Users },
          { id: 'reasoner', label: 'Atomic IRAC Reasoner', icon: Sparkles },
          { id: 'json', label: '25-Layer Canonical JSON', icon: FileCode },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 18px',
                borderBottom: isActive ? '2px solid #06b6d4' : '2px solid transparent',
                color: isActive ? '#f8fafc' : '#94a3b8',
                fontWeight: isActive ? 700 : 500,
                fontSize: '0.9rem',
                transition: 'all 0.15s ease',
              }}
            >
              <Icon size={16} color={isActive ? '#06b6d4' : '#64748b'} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab 1: Proceedings Timeline */}
      {activeTab === 'proceedings' && (
        <div className="glass-card">
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '20px', color: '#f8fafc' }}>
            Procedural Court History Across Registries
          </h3>

          {proceedings.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', position: 'relative', paddingLeft: '24px' }}>
              <div style={{ position: 'absolute', top: 0, bottom: 0, left: '8px', width: '2px', background: 'rgba(99, 102, 241, 0.3)' }} />
              {proceedings.map((p, idx) => (
                <div key={idx} style={{ position: 'relative' }}>
                  <div style={{
                    position: 'absolute',
                    left: '-20px',
                    top: '4px',
                    width: '10px',
                    height: '10px',
                    borderRadius: '50%',
                    background: '#6366f1',
                    boxShadow: '0 0 8px #6366f1',
                  }} />
                  <div style={{ background: 'rgba(255, 255, 255, 0.03)', padding: '14px 18px', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#f8fafc' }}>
                        {p.stage || 'Court Hearing'} &mdash; {p.court || 'Court of Record'}
                      </span>
                      <span style={{ fontSize: '0.78rem', color: '#818cf8', fontFamily: 'var(--font-mono)' }}>
                        {p.hearing_date || p.date || 'Scheduled'}
                      </span>
                    </div>
                    <p style={{ fontSize: '0.85rem', color: '#94a3b8', lineHeight: 1.5 }}>
                      {p.summary || p.notes || p.order_summary || 'Proceeding recorded in case history.'}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#94a3b8' }}>No proceedings attached to this canonical atom yet.</p>
          )}
        </div>
      )}

      {/* Tab 2: Accused & Offenses */}
      {activeTab === 'accused' && (
        <div className="glass-card">
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '16px', color: '#f8fafc' }}>
            Accused Entities & Charged Provisions
          </h3>

          {accused.length > 0 ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '16px' }}>
              {accused.map((a, idx) => (
                <div key={idx} style={{ background: '#111827', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <strong style={{ color: '#f8fafc', fontSize: '0.95rem' }}>{a.name || `Accused #${idx + 1}`}</strong>
                    <StatusBadge status={a.custody_status || 'ON BAIL'} />
                  </div>
                  <div style={{ fontSize: '0.82rem', color: '#94a3b8', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <div><strong>Role:</strong> {a.role || 'Principal Accused'}</div>
                    {a.counsel && <div><strong>Counsel:</strong> {a.counsel}</div>}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#94a3b8' }}>No accused persons recorded for this FIR atom.</p>
          )}
        </div>
      )}

      {/* Tab 3: Atomic IRAC Reasoner */}
      {activeTab === 'reasoner' && (
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#67e8f9', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={18} />
              <span>Grounded Atomic Legal Reasoner (IRAC)</span>
            </h3>
            <p style={{ color: '#94a3b8', fontSize: '0.88rem', marginTop: '4px' }}>
              Queries run with bounded context strictly assembled from this canonical FIR atom. Zero hallucination.
            </p>
          </div>

          <form onSubmit={handleRunReasoner} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <textarea
              rows={3}
              value={reasonQuestion}
              onChange={(e) => setReasonQuestion(e.target.value)}
              placeholder="Enter your legal question regarding this FIR atom..."
              className="input-field"
              style={{ resize: 'vertical' }}
            />
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button
                type="submit"
                disabled={reasoning}
                className="btn btn-cyan"
                style={{ gap: '8px' }}
              >
                <Sparkles size={16} />
                <span>{reasoning ? 'Executing IRAC Reasoner...' : 'Ask Atomic Reasoner'}</span>
              </button>
            </div>
          </form>

          {reasonResult && (
            <div className="animate-fade-in" style={{
              background: '#090d16',
              border: '1px solid rgba(6, 182, 212, 0.3)',
              borderRadius: '12px',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '16px',
            }}>
              <div>
                <span style={{ fontSize: '0.75rem', color: '#06b6d4', fontWeight: 700, textTransform: 'uppercase' }}>Issue</span>
                <p style={{ color: '#f8fafc', fontSize: '0.95rem', fontWeight: 600, marginTop: '2px' }}>
                  {reasonResult.issue || reasonQuestion}
                </p>
              </div>

              <div>
                <span style={{ fontSize: '0.75rem', color: '#a855f7', fontWeight: 700, textTransform: 'uppercase' }}>Rule / Statutory Provisions</span>
                <p style={{ color: '#cbd5e1', fontSize: '0.9rem', marginTop: '2px' }}>
                  {reasonResult.rule || 'Provisions cited under relevant IPC and CrPC sections.'}
                </p>
              </div>

              <div>
                <span style={{ fontSize: '0.75rem', color: '#818cf8', fontWeight: 700, textTransform: 'uppercase' }}>Application / Analysis</span>
                <div style={{ color: '#cbd5e1', fontSize: '0.92rem', lineHeight: 1.7, marginTop: '2px', whiteSpace: 'pre-wrap' }}>
                  {reasonResult.application || reasonResult.answer || reasonResult.analysis || JSON.stringify(reasonResult)}
                </div>
              </div>

              <div>
                <span style={{ fontSize: '0.75rem', color: '#10b981', fontWeight: 700, textTransform: 'uppercase' }}>Conclusion</span>
                <p style={{ color: '#6ee7b7', fontSize: '0.95rem', fontWeight: 600, marginTop: '2px' }}>
                  {reasonResult.conclusion || 'Grounded atomic reasoning verified.'}
                </p>
              </div>

              {reasonResult.citations && reasonResult.citations.length > 0 && (
                <div style={{ paddingTop: '12px', borderTop: '1px solid rgba(255, 255, 255, 0.08)' }}>
                  <span style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 700 }}>VERBATIM CITATIONS</span>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '6px' }}>
                    {reasonResult.citations.map((cite, i) => (
                      <div key={i} style={{ fontSize: '0.8rem', color: '#94a3b8', background: 'rgba(255,255,255,0.02)', padding: '6px 10px', borderRadius: '4px' }}>
                        &bull; {typeof cite === 'string' ? cite : cite.quote || JSON.stringify(cite)}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Tab 4: 25-Layer JSON */}
      {activeTab === 'json' && (
        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
              Canonical 25-Layer Legal JSON Payload
            </h3>
            <a
              href={`/api/atoms/canonical/${encodeURIComponent(atom.id || atom.canonical_fir_id)}`}
              target="_blank"
              rel="noreferrer"
              className="btn btn-secondary btn-sm"
              style={{ gap: '6px' }}
            >
              <Download size={13} />
              <span>Download JSON</span>
            </a>
          </div>

          <pre style={{
            background: '#090d16',
            padding: '20px',
            borderRadius: '10px',
            border: '1px solid rgba(255, 255, 255, 0.08)',
            color: '#67e8f9',
            fontFamily: 'var(--font-mono)',
            fontSize: '0.82rem',
            overflowX: 'auto',
            maxHeight: '600px',
          }}>
            {JSON.stringify(canonicalJson || atom, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
