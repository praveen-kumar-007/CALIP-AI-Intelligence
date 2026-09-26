import React, { useState, useEffect } from 'react';
import { LoadingSpinner } from '../components/common/LoadingSpinner';
import { StatusBadge } from '../components/common/StatusBadge';
import { api } from '../services/api';
import { ShieldAlert, CheckCircle, ArrowLeft, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';

export function ReviewQueuePage() {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadQueue() {
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
    }
    loadQueue();
  }, []);

  return (
    <div className="container">
      <Link to="/admin" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', color: '#818cf8', fontSize: '0.85rem', marginBottom: '20px' }}>
        <ArrowLeft size={16} /> Back to Admin
      </Link>

      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 800, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
          <ShieldAlert size={26} color="#f59e0b" />
          <span>Human-in-the-Loop Review Queue</span>
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.88rem', marginTop: '4px' }}>
          Records flagged with low confidence, conflicting FIR charges, or ambiguous court citations requiring verification.
        </p>
      </div>

      {loading ? (
        <LoadingSpinner text="Retrieving review queue items..." />
      ) : (
        <div>
          <div style={{ marginBottom: '16px', fontSize: '0.85rem', color: '#64748b' }}>
            Pending items: <strong>{queue.length}</strong>
          </div>

          {queue.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {queue.map((item) => (
                <div key={item.id} className="glass-card" style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '0.78rem', color: '#818cf8', fontFamily: 'var(--font-mono)' }}>
                        ITEM #{item.id}
                      </span>
                      {item.document_id && (
                        <Link to={`/documents/${item.document_id}`} style={{ fontSize: '0.82rem', color: '#06b6d4', fontWeight: 600 }}>
                          Document Ref: {item.document_id} &rarr;
                        </Link>
                      )}
                    </div>
                    <StatusBadge status={item.status || 'PENDING'} />
                  </div>

                  <div>
                    <strong style={{ color: '#f8fafc', fontSize: '0.95rem' }}>Reason: </strong>
                    <span style={{ color: '#cbd5e1' }}>{item.review_reason || 'Low confidence OCR extraction'}</span>
                  </div>

                  {item.detected_data && (
                    <pre style={{
                      background: '#090d16',
                      padding: '12px',
                      borderRadius: '6px',
                      color: '#a5b4fc',
                      fontSize: '0.8rem',
                      fontFamily: 'var(--font-mono)',
                      overflowX: 'auto',
                    }}>
                      {typeof item.detected_data === 'string' ? item.detected_data : JSON.stringify(item.detected_data, null, 2)}
                    </pre>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="glass-card" style={{ textAlign: 'center', padding: '48px 24px' }}>
              <CheckCircle size={36} color="#10b981" style={{ margin: '0 auto 12px' }} />
              <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc' }}>
                All Clear! Zero Pending Conflicts
              </h3>
              <p style={{ color: '#94a3b8', fontSize: '0.88rem', marginTop: '4px' }}>
                All extracted legal records and canonical atoms meet platform confidence thresholds.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
