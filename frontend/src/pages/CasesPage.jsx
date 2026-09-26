import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { CaseCard } from '../components/cases/CaseCard';
import { api } from '../services/api';

export function CasesPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const currentState = searchParams.get('state') || '';
  const currentQuery = searchParams.get('q') || '';

  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCases() {
      try {
        setLoading(true);
        const data = await api.getCases(currentState, '', 100);
        setCases(Array.isArray(data) ? data : data?.cases || data?.items || []);
      } catch (err) {
        console.error('Failed loading cases:', err);
      } finally {
        setLoading(false);
      }
    }
    loadCases();
  }, [currentState, currentQuery]);

  const states = [
    { label: 'All Jurisdictions (45)', value: '' },
    { label: 'Maharashtra (12)', value: 'Maharashtra' },
    { label: 'Gujarat (13)', value: 'Gujarat' },
    { label: 'Delhi (2)', value: 'Delhi' },
    { label: 'Kolkata (3)', value: 'Kolkata' },
    { label: 'Supreme Court (4)', value: 'Supreme Court' },
    { label: 'High Court (5)', value: 'High Court' },
  ];

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800, color: 'var(--text-main)', marginBottom: '0.5rem' }}>
            Legal Cases Repository
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>
            Authoritative index of criminal and civil cases from Maharashtra, Gujarat, Delhi, Kolkata, and Apex Courts.
          </p>
        </div>
        <div style={{ fontSize: '0.9rem', color: 'var(--text-dim)' }}>
          Showing <strong style={{ color: 'var(--text-main)' }}>{cases.length}</strong> legal cases
        </div>
      </div>

      {/* Category Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', overflowX: 'auto', paddingBottom: '1rem', marginBottom: '2rem' }}>
        {states.map((tab, idx) => {
          const isActive = currentState === tab.value;
          return (
            <button
              key={idx}
              onClick={() => {
                if (tab.value) {
                  setSearchParams({ state: tab.value });
                } else {
                  setSearchParams({});
                }
              }}
              className={`btn ${isActive ? 'btn-primary' : 'btn-secondary'} btn-sm`}
              style={{ whiteSpace: 'nowrap' }}
            >
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Cases Grid */}
      <div className="card-grid">
        {cases.map((caseItem) => (
          <CaseCard key={caseItem.id} caseItem={caseItem} />
        ))}
      </div>
    </>
  );
}
