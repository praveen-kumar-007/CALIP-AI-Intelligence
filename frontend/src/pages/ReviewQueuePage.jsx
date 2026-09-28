import React, { useState, useEffect } from 'react';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { StatusBadge } from '../components/common/StatusBadge';
import { api } from '../services/api';
import { ShieldAlert, CheckCircle, ArrowLeft, Check, Edit3, XCircle, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';

export function ReviewQueuePage() {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editJson, setEditJson] = useState('');
  const [actionInProgress, setActionInProgress] = useState(null);
  const [bannerMessage, setBannerMessage] = useState(null);

  const loadQueue = async () => {
    try {
      setLoading(true);
      const data = await api.getReviewQueue();
      setQueue(data?.items || []);
    } catch (err) {
      console.error('Failed loading review queue:', err);
      setQueue([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQueue();
  }, []);

  const handleApprove = async (itemId) => {
    try {
      setActionInProgress(itemId);
      await api.approveReviewItem(itemId, 'Verified by advocate reviewer', 'Advocate Reviewer');
      setBannerMessage({ type: 'success', text: `Item #${itemId} successfully approved and committed to atom.` });
      setQueue((prev) => prev.filter((item) => item.id !== itemId));
    } catch (err) {
      setBannerMessage({ type: 'error', text: `Failed to approve item: ${err.message}` });
    } finally {
      setActionInProgress(null);
      setTimeout(() => setBannerMessage(null), 4000);
    }
  };

  const handleStartEdit = (item) => {
    setEditingId(item.id);
    const jsonStr = typeof item.detected_data === 'string'
      ? item.detected_data
      : JSON.stringify(item.detected_data || {}, null, 2);
    setEditJson(jsonStr);
  };

  const handleSaveCorrection = async (itemId) => {
    try {
      setActionInProgress(itemId);
      let parsedData;
      try {
        parsedData = JSON.parse(editJson);
      } catch {
        alert('Invalid JSON formatting. Please check syntax before saving.');
        setActionInProgress(null);
        return;
      }
      await api.correctReviewItem(itemId, parsedData, 'Manual correction applied by advocate', 'Advocate Reviewer');
      setBannerMessage({ type: 'success', text: `Item #${itemId} updated and marked as corrected.` });
      setEditingId(null);
      setQueue((prev) => prev.filter((item) => item.id !== itemId));
    } catch (err) {
      setBannerMessage({ type: 'error', text: `Failed to correct item: ${err.message}` });
    } finally {
      setActionInProgress(null);
      setTimeout(() => setBannerMessage(null), 4000);
    }
  };

  const handleDispute = async (itemId) => {
    const reason = prompt('Please enter dispute reason / contradiction note:');
    if (!reason) return;
    try {
      setActionInProgress(itemId);
      await api.disputeReviewItem(itemId, reason, 'Advocate Reviewer');
      setBannerMessage({ type: 'success', text: `Item #${itemId} recorded as disputed.` });
      setQueue((prev) => prev.filter((item) => item.id !== itemId));
    } catch (err) {
      setBannerMessage({ type: 'error', text: `Failed to dispute item: ${err.message}` });
    } finally {
      setActionInProgress(null);
      setTimeout(() => setBannerMessage(null), 4000);
    }
  };

  return (
    <div className="container" style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px' }}>
      <Link to="/admin" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: '#818cf8', fontSize: '0.85rem', marginBottom: '20px' }}>
        <ArrowLeft size={16} /> Back to Admin
      </Link>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px', marginBottom: '28px' }}>
        <div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <ShieldAlert size={26} color="#f59e0b" />
            <span>Human-in-the-Loop Review Queue</span>
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '0.88rem', marginTop: '4px' }}>
            Records flagged with low OCR confidence, conflicting statutory charges, or ambiguous court coordinates requiring advocate sign-off.
          </p>
        </div>

        <button onClick={loadQueue} className="btn btn-secondary btn-sm" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
          <RefreshCw size={14} /> Refresh Queue
        </button>
      </div>

      {bannerMessage && (
        <div style={{
          padding: '12px 16px',
          borderRadius: '8px',
          marginBottom: '20px',
          fontSize: '0.9rem',
          fontWeight: 600,
          background: bannerMessage.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
          color: bannerMessage.type === 'success' ? '#34d399' : '#f87171',
          border: `1px solid ${bannerMessage.type === 'success' ? '#059669' : '#dc2626'}`,
        }}>
          {bannerMessage.text}
        </div>
      )}

      {loading ? (
        <LoadingSpinner text="Retrieving review queue items..." />
      ) : (
        <div>
          <div style={{ marginBottom: '16px', fontSize: '0.88rem', color: '#64748b' }}>
            Pending Items: <strong style={{ color: '#f8fafc' }}>{queue.length}</strong>
          </div>

          {queue.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
              {queue.map((item) => (
                <div key={item.id} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '12px', padding: '20px', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span style={{ fontSize: '0.82rem', color: '#818cf8', fontFamily: 'monospace', fontWeight: 700 }}>
                        ITEM #{item.id}
                      </span>
                      {item.document_id && (
                        <Link to={`/documents/${item.document_id}`} style={{ fontSize: '0.84rem', color: '#06b6d4', fontWeight: 600 }}>
                          Document: {item.document_id} &rarr;
                        </Link>
                      )}
                    </div>
                    <StatusBadge status={item.status || 'PENDING'} />
                  </div>

                  <div>
                    <strong style={{ color: '#f8fafc', fontSize: '0.95rem' }}>Review Trigger: </strong>
                    <span style={{ color: '#cbd5e1' }}>{item.review_reason || 'Low confidence OCR extraction'}</span>
                  </div>

                  {editingId === item.id ? (
                    <div>
                      <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '6px' }}>Edit Extracted JSON:</div>
                      <textarea
                        value={editJson}
                        onChange={(e) => setEditJson(e.target.value)}
                        style={{
                          width: '100%',
                          minHeight: '160px',
                          background: '#090d16',
                          color: '#38bdf8',
                          padding: '12px',
                          borderRadius: '8px',
                          fontFamily: 'monospace',
                          fontSize: '0.85rem',
                          border: '1px solid #3b82f6',
                        }}
                      />
                      <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                        <button
                          onClick={() => handleSaveCorrection(item.id)}
                          disabled={actionInProgress === item.id}
                          className="btn btn-primary btn-sm"
                        >
                          <Check size={14} /> Save &amp; Mark Corrected
                        </button>
                        <button
                          onClick={() => setEditingId(null)}
                          className="btn btn-secondary btn-sm"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    item.detected_data && (
                      <pre style={{
                        background: '#090d16',
                        padding: '14px',
                        borderRadius: '8px',
                        color: '#a5b4fc',
                        fontSize: '0.82rem',
                        fontFamily: 'monospace',
                        overflowX: 'auto',
                        border: '1px solid rgba(255, 255, 255, 0.05)',
                      }}>
                        {typeof item.detected_data === 'string' ? item.detected_data : JSON.stringify(item.detected_data, null, 2)}
                      </pre>
                    )
                  )}

                  {editingId !== item.id && (
                    <div style={{ display: 'flex', gap: '10px', marginTop: '4px', flexWrap: 'wrap' }}>
                      <button
                        onClick={() => handleApprove(item.id)}
                        disabled={actionInProgress === item.id}
                        className="btn btn-sm"
                        style={{ background: '#10b981', color: '#ffffff', display: 'inline-flex', alignItems: 'center', gap: '6px', fontWeight: 600 }}
                      >
                        <Check size={14} /> Approve Extraction
                      </button>
                      <button
                        onClick={() => handleStartEdit(item)}
                        disabled={actionInProgress === item.id}
                        className="btn btn-secondary btn-sm"
                        style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                      >
                        <Edit3 size={14} /> Correct Data
                      </button>
                      <button
                        onClick={() => handleDispute(item.id)}
                        disabled={actionInProgress === item.id}
                        className="btn btn-sm"
                        style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#f87171', border: '1px solid #ef4444', display: 'inline-flex', alignItems: 'center', gap: '6px' }}
                      >
                        <XCircle size={14} /> Dispute Fact
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="glass-card" style={{ textAlign: 'center', padding: '48px 24px', borderRadius: '12px' }}>
              <CheckCircle size={40} color="#10b981" style={{ margin: '0 auto 12px' }} />
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                All Clear! Zero Pending Conflicts
              </h3>
              <p style={{ color: '#94a3b8', fontSize: '0.88rem', marginTop: '6px' }}>
                All extracted legal records and canonical atoms meet platform confidence thresholds.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
