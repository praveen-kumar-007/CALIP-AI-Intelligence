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
  Copy,
  FileText,
  Download,
  Languages,
  BookOpen,
} from 'lucide-react';

export function AtomDetailPage() {
  const { id } = useParams();
  const { showToast } = useApp();
  const [atom, setAtom] = useState(null);
  const [canonicalJson, setCanonicalJson] = useState(null);
  const [hydration, setHydration] = useState(null);
  const [atomDocs, setAtomDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('bilingual'); // Default to bilingual records!
  const [copySuccess, setCopySuccess] = useState(false);

  // Dynamic Reasoner State
  const [reasonQuestion, setReasonQuestion] = useState('Compare the charges, overt acts alleged, and bail considerations across the accused in a structured table.');
  const [reasonResult, setReasonResult] = useState(null);
  const [reasoning, setReasoning] = useState(false);

  useEffect(() => {
    async function loadAtom() {
      try {
        setLoading(true);
        const [atomRes, jsonRes, hydRes, docsRes] = await Promise.allSettled([
          api.getAtomById(id),
          api.getCanonicalAtom(id),
          api.getAtomHydration(id),
          api.getAtomDocuments(id),
        ]);

        if (atomRes.status === 'fulfilled') setAtom(atomRes.value);
        if (jsonRes.status === 'fulfilled') setCanonicalJson(jsonRes.value);
        if (hydRes.status === 'fulfilled') setHydration(hydRes.value);
        if (docsRes.status === 'fulfilled' && docsRes.value?.documents) {
          setAtomDocs(docsRes.value.documents);
        }
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
      showToast('Dynamic legal briefing generated!', 'success');
    } catch (err) {
      console.error('Reasoning failed:', err);
      showToast(err.message || 'Reasoning query failed', 'error');
    } finally {
      setReasoning(false);
    }
  };

  const handleCopyAnalysis = () => {
    if (!reasonResult?.answer) return;
    navigator.clipboard.writeText(reasonResult.answer);
    setCopySuccess(true);
    showToast('Analysis copied to clipboard!', 'success');
    setTimeout(() => setCopySuccess(false), 2000);
  };

  if (loading) return <LoadingSpinner text="Retrieving 25-layer cognitive atom dossier..." />;

  if (!atom) {
    return (
      <div className="container" style={{ textAlign: 'center', padding: '64px 0' }}>
        <h2>Legal Atom Not Found</h2>
        <Link to="/atoms" className="btn btn-primary" style={{ marginTop: '20px' }}>
          <ArrowLeft size={16} /> Back to 24 Pilot Atoms
        </Link>
      </div>
    );
  }

  const proceedings = atom.proceedings || canonicalJson?.case_lineage || canonicalJson?.proceedings || [];
  const accused = atom.accused || canonicalJson?.accused || [];
  const bilingualData = canonicalJson?.bilingual_matrix || {};
  const nativeSummary = bilingualData.original_script_summary || canonicalJson?.fir?.original_native_text || atom.original_language_summary || atom.summary || '';
  const englishSummary = bilingualData.english_translated_summary || canonicalJson?.fir?.english_translated_text || atom.english_translated_summary || atom.summary || '';
  const allegationsList = bilingualData.allegations || canonicalJson?.core_allegations || canonicalJson?.allegations || [];

  return (
    <div className="container" style={{ maxWidth: '1400px', margin: '0 auto', padding: '16px 20px 48px' }}>
      {/* Back button */}
      <Link
        to="/atoms"
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          color: '#1d4ed8',
          fontSize: '0.88rem',
          fontWeight: 600,
          marginBottom: '20px',
          padding: '6px 14px',
          borderRadius: '6px',
          background: '#eff6ff',
          border: '1px solid #bfdbfe',
          transition: 'all 0.2s ease',
        }}
      >
        <ArrowLeft size={16} /> Back to 24 Pilot Atoms Directory
      </Link>

      {/* Hero Dossier Card */}
      <div
        className="glass-card"
        style={{
          background: '#ffffff',
          border: '1px solid #e2e8f0',
          boxShadow: '0 4px 16px -2px rgba(15, 23, 42, 0.06)',
          marginBottom: '24px',
          padding: '28px',
          borderRadius: '16px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px', flexWrap: 'wrap' }}>
              <span style={{
                fontSize: '0.74rem',
                fontFamily: 'var(--font-mono)',
                color: '#1d4ed8',
                background: '#eff6ff',
                border: '1px solid #bfdbfe',
                padding: '3px 10px',
                borderRadius: '6px',
                fontWeight: 700,
                letterSpacing: '0.04em',
              }}>
                CANONICAL FIR ATOM
              </span>
              <span className="badge badge-indigo" style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '5px' }}>
                <Languages size={13} />
                {atom.original_language || 'Marathi (मराठी)'}
              </span>
              <StatusBadge status={atom.hydration_status || 'HYDRATED'} />
            </div>

            <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#0f172a', lineHeight: 1.25, marginBottom: '6px', letterSpacing: '-0.02em' }}>
              {atom.canonical_fir_id || `FIR-${atom.id}`}
            </h1>
            <p style={{ color: '#475569', fontSize: '0.94rem', margin: 0 }}>
              {atom.police_station} Police Station &bull; District {atom.district}, State {atom.state} &bull; FIR {atom.fir_number} of {atom.fir_year}
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
            <button
              onClick={() => setActiveTab('reasoner')}
              className="btn btn-primary btn-sm"
              style={{ gap: '6px', padding: '0.5rem 1.1rem', fontSize: '0.85rem' }}
            >
              <Sparkles size={15} />
              <span>Dynamic AI Reasoner</span>
            </button>
            <a
              href={`/api/atoms/canonical/${encodeURIComponent(atom.id || atom.canonical_fir_id)}`}
              target="_blank"
              rel="noreferrer"
              className="btn btn-secondary btn-sm"
              style={{ gap: '6px', padding: '0.5rem 1.1rem', fontSize: '0.85rem' }}
            >
              <FileCode size={15} />
              <span>25-Layer JSON</span>
            </a>
          </div>
        </div>

        {/* 5-Column Metadata Micro-Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '12px',
          marginTop: '22px',
          paddingTop: '20px',
          borderTop: '1px solid #f1f5f9',
        }}>
          <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '12px 16px' }}>
            <span style={{ color: '#64748b', display: 'block', fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.05em', marginBottom: '4px' }}>POLICE STATION</span>
            <strong style={{ color: '#0f172a', fontSize: '0.95rem' }}>{atom.police_station || 'Central Station'}</strong>
          </div>
          <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '12px 16px' }}>
            <span style={{ color: '#64748b', display: 'block', fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.05em', marginBottom: '4px' }}>STATE / JURISDICTION</span>
            <strong style={{ color: '#0f172a', fontSize: '0.95rem' }}>{atom.state || 'MH'} ({atom.district})</strong>
          </div>
          <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '12px 16px' }}>
            <span style={{ color: '#64748b', display: 'block', fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.05em', marginBottom: '4px' }}>REGISTRATION LANGUAGE</span>
            <strong style={{ color: '#1d4ed8', fontSize: '0.95rem' }}>{atom.original_language || 'Marathi (मराठी)'}</strong>
          </div>
          <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '12px 16px' }}>
            <span style={{ color: '#64748b', display: 'block', fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.05em', marginBottom: '4px' }}>SECTIONS REGISTERED</span>
            <strong style={{ color: '#0f172a', fontSize: '0.95rem' }}>{atom.sections_registered || 'IPC 420, 406'}</strong>
          </div>
          <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '12px 16px' }}>
            <span style={{ color: '#64748b', display: 'block', fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.05em', marginBottom: '4px' }}>VERIFICATION CONFIDENCE</span>
            <span style={{ color: '#059669', fontWeight: 800, fontSize: '0.95rem' }}>
              {atom.confidence_score !== undefined && atom.confidence_score !== null ? `${(atom.confidence_score * 100).toFixed(0)}% Verified` : 'Pending Verification'}
            </span>
          </div>
        </div>
      </div>

      {/* Segmented Pill Navigation Bar */}
      <div
        style={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: '8px',
          background: '#f1f5f9',
          padding: '6px',
          borderRadius: '12px',
          border: '1px solid #e2e8f0',
          marginBottom: '24px',
        }}
      >
        {[
          { id: 'bilingual', label: `Bilingual Records (${atom.original_language || 'Native/English'})`, icon: Languages },
          { id: 'proceedings', label: `Proceedings Timeline (${proceedings.length})`, icon: Calendar },
          { id: 'accused', label: `Accused & Offenses (${accused.length})`, icon: Users },
          { id: 'documents', label: `Documents & Exhibits (${atomDocs.length || atom.doc_count || 0})`, icon: Layers },
          { id: 'reasoner', label: 'Dynamic Legal Reasoner', icon: Sparkles },
          { id: 'json', label: '25-Layer Canonical JSON', icon: FileCode },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '9px 16px',
                borderRadius: '8px',
                background: isActive
                  ? '#ffffff'
                  : 'transparent',
                border: isActive ? '1px solid #cbd5e1' : '1px solid transparent',
                color: isActive ? '#1d4ed8' : '#64748b',
                fontWeight: isActive ? 700 : 500,
                fontSize: '0.88rem',
                cursor: 'pointer',
                transition: 'all 0.18s ease',
                boxShadow: isActive ? '0 1px 3px rgba(15, 23, 42, 0.08)' : 'none',
              }}
            >
              <Icon size={16} color={isActive ? '#1d4ed8' : '#64748b'} />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab 1: Bilingual Records (Original Native Script + English Translation) */}
      {activeTab === 'bilingual' && (
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '24px', padding: '28px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', marginBottom: '8px' }}>
              <h3 style={{ fontSize: '1.3rem', fontWeight: 800, color: '#0f172a', display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Languages size={22} color="#1d4ed8" />
                <span>Bilingual Evidentiary Records &amp; Vernacular Separation</span>
              </h3>
              <span className="badge badge-indigo" style={{ fontSize: '0.82rem', padding: '6px 14px' }}>
                Original Language: {atom.original_language || 'Marathi (मराठी)'}
              </span>
            </div>
            <p style={{ color: '#475569', fontSize: '0.92rem', margin: 0, lineHeight: 1.6 }}>
              CALIP preserves and stores regional native language text (Devanagari, Gujarati, Bengali, etc.) verbatim in its authentic script, alongside authoritative English legal translations for full evidentiary transparency.
            </p>
          </div>

          {/* Side-by-side Dual Comparison Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '20px' }}>
            {/* Native Script Card */}
            <div style={{
              background: '#ffffff',
              border: '1.5px solid #bfdbfe',
              borderRadius: '12px',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '14px',
              boxShadow: '0 2px 8px rgba(15, 23, 42, 0.04)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#1d4ed8', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  Authentic Native Script (Original Form)
                </span>
                <span className="badge badge-indigo" style={{ fontSize: '0.74rem' }}>
                  {atom.original_language || 'Vernacular'}
                </span>
              </div>
              <div style={{
                fontSize: '1.05rem',
                lineHeight: 2.0,
                color: '#0f172a',
                whiteSpace: 'pre-wrap',
                fontFamily: "'Noto Sans Devanagari', 'Mukta', sans-serif",
                background: '#f8fafc',
                padding: '18px',
                borderRadius: '8px',
                border: '1px solid #e2e8f0',
              }}>
                {nativeSummary || 'स्थानिक भाषेतील प्रथम माहिती अहवाल (FIR) तपशील.'}
              </div>
            </div>

            {/* Verified English Translation Card */}
            <div style={{
              background: '#ffffff',
              border: '1.5px solid #bbf7d0',
              borderRadius: '12px',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '14px',
              boxShadow: '0 2px 8px rgba(15, 23, 42, 0.04)',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#047857', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  Authoritative English Legal Translation
                </span>
                <span className="badge badge-emerald" style={{ fontSize: '0.74rem' }}>
                  Verified English
                </span>
              </div>
              <div style={{
                fontSize: '0.98rem',
                lineHeight: 1.85,
                color: '#0f172a',
                whiteSpace: 'pre-wrap',
                background: '#f8fafc',
                padding: '18px',
                borderRadius: '8px',
                border: '1px solid #e2e8f0',
              }}>
                {englishSummary || 'Authoritative English translation of canonical FIR record.'}
              </div>
            </div>
          </div>

          {/* Structured Bilingual Allegations Table */}
          {allegationsList.length > 0 && (
            <div style={{ marginTop: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
                <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
                  Bilingual Allegations Matrix (Native vs English)
                </h4>
                <span className="badge badge-indigo">{allegationsList.length} Allegations Grounded</span>
              </div>
              <div className="table-responsive-wrapper">
                <table className="legal-table" style={{ background: '#ffffff', border: '1px solid #e2e8f0' }}>
                  <thead>
                    <tr style={{ background: '#f8fafc' }}>
                      <th style={{ width: '45%', color: '#475569' }}>Original Native Script ({atom.original_language || 'Native'})</th>
                      <th style={{ width: '45%', color: '#475569' }}>Verified English Legal Translation</th>
                      <th style={{ width: '10%', color: '#475569' }}>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {allegationsList.map((al, idx) => (
                      <tr key={idx}>
                        <td style={{ color: '#0f172a', fontFamily: "'Noto Sans Devanagari', 'Mukta', sans-serif", fontSize: '0.98rem', lineHeight: 1.8 }}>
                          {al.native_script || al.original_language_text || al.original_native_script || al.text}
                        </td>
                        <td style={{ color: '#1e293b', fontSize: '0.92rem', lineHeight: 1.7 }}>
                          {al.english_translation || al.english_translated_text || al.text}
                        </td>
                        <td>
                          <span className="badge badge-indigo" style={{ fontSize: '0.74rem' }}>{al.status || 'ALLEGED'}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Proceedings Timeline */}
      {activeTab === 'proceedings' && (
        <div className="glass-card">
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '20px', color: '#0f172a' }}>
            Procedural Court History Across Registries
          </h3>

          {proceedings.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', position: 'relative', paddingLeft: '24px' }}>
              <div style={{ position: 'absolute', top: 0, bottom: 0, left: '8px', width: '2px', background: '#cbd5e1' }} />
              {proceedings.map((p, idx) => (
                <div key={idx} style={{ position: 'relative' }}>
                  <div style={{
                    position: 'absolute',
                    left: '-20px',
                    top: '6px',
                    width: '10px',
                    height: '10px',
                    borderRadius: '50%',
                    background: '#2563eb',
                    boxShadow: '0 0 4px #2563eb',
                  }} />
                  <div style={{ background: '#f8fafc', padding: '14px 18px', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                      <span style={{ fontSize: '0.88rem', fontWeight: 700, color: '#0f172a' }}>
                        {p.court_tier || p.tier || 'COURT'} &mdash; {p.court_name || p.court || 'Court of Record'}
                      </span>
                      <span style={{ fontSize: '0.78rem', color: '#1d4ed8', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                        Case: {p.case_number || 'CC Pending'}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.82rem', color: '#64748b', display: 'flex', gap: '16px' }}>
                      <span><strong>Status:</strong> <span className="badge badge-cyan" style={{ fontSize: '0.72rem' }}>{p.status || 'PENDING'}</span></span>
                      {p.filing_date && <span><strong>Filing:</strong> {p.filing_date}</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#64748b' }}>No proceedings attached to this canonical atom yet.</p>
          )}
        </div>
      )}

      {/* Tab 3: Accused & Offenses */}
      {activeTab === 'accused' && (
        <div className="glass-card">
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '16px', color: '#0f172a' }}>
            Accused Profiles &amp; Charged Provisions
          </h3>

          {accused.length > 0 ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '16px' }}>
              {accused.map((a, idx) => (
                <div key={idx} style={{ background: '#f8fafc', padding: '16px', borderRadius: '10px', border: '1px solid #e2e8f0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <strong style={{ color: '#0f172a', fontSize: '0.95rem' }}>
                      [{a.code || a.accused_code || `A${idx + 1}`}] {a.canonical_name || a.name || `Accused #${idx + 1}`}
                    </strong>
                    <StatusBadge status={a.custody_status || 'ON BAIL'} />
                  </div>
                  <div style={{ fontSize: '0.82rem', color: '#64748b', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <div><strong>Custody Duration:</strong> {a.custody_days || 0} Days</div>
                    {a.aliases && a.aliases.length > 0 && (
                      <div><strong>Aliases:</strong> {a.aliases.join(', ')}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#64748b' }}>No accused persons recorded for this FIR atom.</p>
          )}
        </div>
      )}

      {/* Tab 4: Documents & Evidentiary Records */}
      {activeTab === 'documents' && (
        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px' }}>
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
                Evidentiary Documents ({atomDocs.length})
              </h3>
              <p style={{ color: '#64748b', fontSize: '0.85rem', marginTop: '4px' }}>
                Primary legal PDFs, charge sheets, gazette rules, and seizure records linked to this Canonical Atom.
              </p>
            </div>
          </div>

          {atomDocs.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {atomDocs.map((doc, idx) => (
                <div key={idx} style={{
                  background: '#f8fafc',
                  border: '1px solid #e2e8f0',
                  borderRadius: '10px',
                  padding: '16px 20px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  flexWrap: 'wrap',
                  gap: '12px',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{
                      width: 40,
                      height: 40,
                      borderRadius: 8,
                      background: '#eff6ff',
                      border: '1px solid #bfdbfe',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#1d4ed8',
                    }}>
                      <FileText size={20} />
                    </div>
                    <div>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
                        {doc.title}
                      </h4>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '4px', fontSize: '0.8rem', color: '#64748b' }}>
                        <span>Pages: <strong style={{ color: doc.page_count > 0 ? '#1d4ed8' : '#64748b' }}>
                          {doc.page_count > 0 ? `${doc.page_count} Pages` : '-'}
                        </strong></span>
                        <span>&bull;</span>
                        <span className="badge badge-emerald" style={{ fontSize: '0.7rem' }}>{doc.ocr_status || 'EXTRACTED'}</span>
                        <span>&bull;</span>
                        <span className="badge badge-indigo" style={{ fontSize: '0.7rem' }}>{doc.detected_language || 'English'}</span>
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    <a
                      href={
                        doc.original_pdf_url ||
                        doc.pdf_url ||
                        (doc.id ? `https://longtailcases.com/uploads/files/${doc.id.replace(/^doc-/, '').replace(/_pdf$/, '.pdf')}` : 'https://longtailcases.com')
                      }
                      target="_blank"
                      rel="noreferrer"
                      className="btn btn-secondary btn-sm"
                      style={{
                        background: '#eff6ff',
                        borderColor: '#93c5fd',
                        color: '#1d4ed8',
                        fontWeight: 700,
                        gap: '6px',
                        display: 'inline-flex',
                        alignItems: 'center',
                      }}
                      title="Open authentic original PDF directly on longtailcases.com"
                    >
                      <Download size={13} />
                      <span>🔗 Source PDF (longtailcases) ↗</span>
                    </a>

                    <Link to={`/documents/${doc.id}`} className="btn btn-primary btn-sm" style={{ gap: '6px' }}>
                      <BookOpen size={13} />
                      <span>Inspect OCR &amp; Text</span>
                    </Link>

                    <a href={`/documents/${doc.id}/download/txt`} className="btn btn-secondary btn-sm" title="Download Plain Text">
                      <span>TXT ↓</span>
                    </a>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#64748b' }}>No separate document records currently linked to this atom.</p>
          )}
        </div>
      )}

      {/* Tab 5: Dynamic Legal Reasoner (Decided by LLM: Tables, Timelines, Bilingual Cards) */}
      {activeTab === 'reasoner' && (
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#1d4ed8', display: 'flex', alignItems: 'center', gap: '8px', margin: 0 }}>
                <Sparkles size={18} />
                <span>Dynamic Legal Reasoner (Unconstrained Adaptive Formats)</span>
              </h3>
              <span className="badge badge-indigo">Adaptive Presentation (Tables / Timelines / Bilingual)</span>
            </div>
            <p style={{ color: '#475569', fontSize: '0.88rem', marginTop: '6px', margin: 0 }}>
              Based on your legal question, CALIP's LLM automatically formats the response in the optimal presentation style (comparative tables, chronological timelines, bilingual cards, or structured briefings). Zero rigid boxes.
            </p>
          </div>

          <form onSubmit={handleRunReasoner} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <textarea
              rows={3}
              value={reasonQuestion}
              onChange={(e) => setReasonQuestion(e.target.value)}
              placeholder="Ask a question (e.g. Compare charges across accused in a table, or show bilingual Marathi/English allegations)..."
              className="search-input"
              style={{ resize: 'vertical', width: '100%', borderRadius: '8px' }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                <button
                  type="button"
                  onClick={() => setReasonQuestion('Provide a comparative Markdown Table of all accused, their specific statutory charges, and alleged overt acts.')}
                  className="btn btn-secondary btn-sm"
                  style={{ fontSize: '0.78rem' }}
                >
                  📊 Accused Comparison Table
                </button>
                <button
                  type="button"
                  onClick={() => setReasonQuestion('Show the authentic native language statements alongside their verified English translations in a bilingual table.')}
                  className="btn btn-secondary btn-sm"
                  style={{ fontSize: '0.78rem' }}
                >
                  🌐 Bilingual Translation Matrix
                </button>
                <button
                  type="button"
                  onClick={() => setReasonQuestion('What is the step-by-step procedural timeline across courts from FIR registration to date?')}
                  className="btn btn-secondary btn-sm"
                  style={{ fontSize: '0.78rem' }}
                >
                  ⏱ Procedural Timeline
                </button>
              </div>

              <button
                type="submit"
                disabled={reasoning}
                className="btn btn-primary"
                style={{ gap: '8px' }}
              >
                <Sparkles size={16} />
                <span>{reasoning ? 'Synthesizing Adaptive Analysis...' : 'Ask Atomic Reasoner'}</span>
              </button>
            </div>
          </form>

          {/* Dynamic Rendered Briefing Card */}
          {reasonResult && (
            <div className="animate-fade-in" style={{
              background: '#ffffff',
              border: '1.5px solid #bfdbfe',
              borderRadius: '12px',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              gap: '18px',
              boxShadow: '0 4px 16px rgba(37, 99, 235, 0.08)',
            }}>
              {/* Header Bar */}
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', borderBottom: '1px solid #e2e8f0', paddingBottom: '14px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span className="badge badge-emerald" style={{ padding: '4px 10px', fontSize: '0.78rem', fontWeight: 700 }}>
                    Official Atomic Briefing
                  </span>
                  <span style={{ fontSize: '0.82rem', color: '#64748b' }}>
                    Grounded in Atom: <strong style={{ color: '#1d4ed8' }}>{atom.canonical_fir_id}</strong>
                  </span>
                </div>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button
                    type="button"
                    onClick={handleCopyAnalysis}
                    className="btn btn-secondary btn-sm"
                    style={{ fontSize: '0.8rem', gap: '6px' }}
                  >
                    <Copy size={13} />
                    <span>{copySuccess ? 'Copied!' : 'Copy Analysis'}</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => window.print()}
                    className="btn btn-secondary btn-sm"
                    style={{ fontSize: '0.8rem' }}
                  >
                    Print / PDF
                  </button>
                </div>
              </div>

              {/* Dynamic Content (Adaptive Layout: Tables, Lists, Timelines, Bilingual Cards) */}
              <div className="legal-briefing-body" style={{ color: '#1e293b', fontSize: '0.94rem', lineHeight: 1.8 }}>
                {reasonResult.rendered_html ? (
                  <div dangerouslySetInnerHTML={{ __html: reasonResult.rendered_html }} />
                ) : (
                  <div style={{ whiteSpace: 'pre-wrap' }}>{reasonResult.answer}</div>
                )}
              </div>

              {/* Evidentiary Citations Panel */}
              {reasonResult.sources && reasonResult.sources.length > 0 && (
                <div style={{ paddingTop: '16px', borderTop: '1px solid #e2e8f0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                    <span style={{ fontSize: '0.78rem', color: '#1d4ed8', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      Evidentiary Source Citations ({reasonResult.sources.length} Grounded Snippets)
                    </span>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {reasonResult.sources.map((src, i) => {
                      const docId = src.document_id || src.doc_id || '';
                      const sourcePdfUrl =
                        src.original_pdf_url ||
                        (docId ? `https://longtailcases.com/uploads/files/${docId.replace(/^doc-/, '').replace(/_pdf$/, '.pdf')}` : 'https://longtailcases.com');
                      return (
                        <div key={i} style={{ fontSize: '0.82rem', color: '#334155', background: '#f8fafc', padding: '10px 14px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px', flexWrap: 'wrap', gap: '6px' }}>
                            <strong style={{ color: '#0f172a' }}>
                              [{i + 1}] {src.document_title || src.title || 'Court Record'}
                            </strong>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                              {src.page_number && <span className="badge badge-cyan" style={{ fontSize: '0.7rem' }}>Page {src.page_number}</span>}
                              <a
                                href={sourcePdfUrl}
                                target="_blank"
                                rel="noreferrer"
                                style={{ fontSize: '0.74rem', color: '#2563eb', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '3px' }}
                                title="Open authentic source PDF directly on longtailcases.com"
                              >
                                <span>🔗 longtail PDF ↗</span>
                              </a>
                            </div>
                          </div>
                          {src.chunk_text && (
                            <p style={{ margin: 0, color: '#475569', fontSize: '0.82rem', lineHeight: 1.5 }}>
                              {src.chunk_text.slice(0, 240)}...
                            </p>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Tab 6: 25-Layer JSON */}
      {activeTab === 'json' && (
        <div className="glass-card">
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
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
            background: '#0f172a',
            padding: '20px',
            borderRadius: '10px',
            border: '1px solid #334155',
            color: '#38bdf8',
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
