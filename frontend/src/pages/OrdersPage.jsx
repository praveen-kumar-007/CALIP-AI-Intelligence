import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';

export function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadOrders() {
      try {
        setLoading(true);
        const data = await api.getOrders('', 60);
        setOrders(Array.isArray(data) ? data : data?.orders || data?.items || []);
      } catch (err) {
        console.error('Error loading orders:', err);
      } finally {
        setLoading(false);
      }
    }
    loadOrders();
  }, []);

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
            Court Orders &amp; Directions
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>
            Interim and final judicial orders, bail directions, roznama orders, and split-of-chargesheet directives.
          </p>
        </div>
        <div style={{ fontSize: '0.9rem', color: 'var(--text-dim)' }}>
          Showing <strong style={{ color: 'var(--text-main)' }}>{orders.length}</strong> orders
        </div>
      </div>

      <div className="card-grid">
        {orders.map((o) => (
          <div className="legal-card" key={o.id}>
            <div className="card-header">
              <div>
                <span className="badge badge-cyan" style={{ marginBottom: '0.35rem' }}>
                  {o.order_type || 'Court Order'}
                </span>
                <h2 className="card-title">
                  <Link to={`/documents/${o.id || o.document_id}`}>
                    {o.title || `Order in Case ${o.case_id || ''}`}
                  </Link>
                </h2>
              </div>
              <span className="badge badge-emerald">{o.order_date || o.date || 'Recorded'}</span>
            </div>

            <div className="meta-row">
              <div className="meta-item">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                </svg>
                <span>{o.court || 'District Court'}</span>
              </div>
              {o.bench && (
                <div className="meta-item">
                  <span>Bench: {o.bench}</span>
                </div>
              )}
            </div>

            <p className="card-summary">
              {o.summary || 'Official court order setting procedural dates, bail terms, or discovery directions.'}
            </p>

            <div className="card-footer">
              <Link to={`/cases/${o.case_id}`} style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                Case Record &rarr;
              </Link>
              <Link to={`/documents/${o.id || o.document_id}`} className="btn btn-secondary btn-sm">
                View Order &rarr;
              </Link>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
