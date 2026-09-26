import React, { useState } from 'react';
import { Search, Sparkles, Filter, Database, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function SearchBar({ onSearch, initialQuery = '', initialType = 'hybrid', showFilters = true }) {
  const [query, setQuery] = useState(initialQuery);
  const [searchType, setSearchType] = useState(initialType);
  const [court, setCourt] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    if (onSearch) {
      onSearch(query, searchType, court);
    } else {
      navigate(`/search?q=${encodeURIComponent(query)}&type=${searchType}${court ? `&court=${encodeURIComponent(court)}` : ''}`);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ width: '100%', maxWidth: '860px', margin: '0 auto' }}>
      <div style={{
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        background: 'rgba(17, 24, 39, 0.95)',
        border: '1px solid rgba(99, 102, 241, 0.35)',
        borderRadius: '16px',
        padding: '6px 8px 6px 18px',
        boxShadow: '0 8px 30px rgba(0, 0, 0, 0.4), 0 0 20px rgba(99, 102, 241, 0.15)',
        transition: 'all 0.25s ease',
      }}>
        <Search size={22} color="#818cf8" style={{ marginRight: '12px', flexShrink: 0 }} />
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search Indian Case Law, Sections, FIRs, Orders, Judgments..."
          style={{
            flex: 1,
            background: 'transparent',
            border: 'none',
            color: '#f8fafc',
            fontSize: '1.05rem',
            fontFamily: 'inherit',
            outline: 'none',
            minWidth: '150px',
          }}
        />

        <button
          type="submit"
          className="btn btn-primary"
          style={{ padding: '10px 22px', borderRadius: '12px' }}
        >
          <span>Search</span>
          <ArrowRight size={16} />
        </button>
      </div>

      {showFilters && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          marginTop: '14px',
          padding: '0 8px',
          fontSize: '0.85rem',
          color: '#94a3b8',
        }}>
          {/* Mode Pill Toggle */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.04em', color: '#64748b', fontWeight: 600 }}>Mode:</span>
            {[
              { id: 'hybrid', label: 'Hybrid AI', icon: Sparkles },
              { id: 'semantic', label: 'Semantic Vector', icon: Database },
              { id: 'keyword', label: 'Keyword / BM25', icon: Filter },
            ].map((mode) => {
              const Icon = mode.icon;
              const isActive = searchType === mode.id;
              return (
                <button
                  type="button"
                  key={mode.id}
                  onClick={() => setSearchType(mode.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '5px',
                    padding: '4px 10px',
                    borderRadius: '20px',
                    fontSize: '0.8rem',
                    fontWeight: 500,
                    background: isActive ? 'rgba(99, 102, 241, 0.25)' : 'rgba(255, 255, 255, 0.04)',
                    color: isActive ? '#c7d2fe' : '#94a3b8',
                    border: isActive ? '1px solid rgba(99, 102, 241, 0.5)' : '1px solid rgba(255, 255, 255, 0.08)',
                    transition: 'all 0.15s ease',
                  }}
                >
                  <Icon size={12} />
                  <span>{mode.label}</span>
                </button>
              );
            })}
          </div>

          {/* Court selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.78rem', color: '#64748b', fontWeight: 600 }}>Jurisdiction:</span>
            <select
              value={court}
              onChange={(e) => setCourt(e.target.value)}
              style={{
                background: '#1e293b',
                border: '1px solid var(--border-subtle)',
                color: '#f8fafc',
                padding: '4px 10px',
                borderRadius: '8px',
                fontSize: '0.82rem',
                outline: 'none',
              }}
            >
              <option value="">All Courts</option>
              <option value="Supreme Court of India">Supreme Court of India</option>
              <option value="Delhi High Court">Delhi High Court</option>
              <option value="Bombay High Court">Bombay High Court</option>
              <option value="Allahabad High Court">Allahabad High Court</option>
              <option value="Madras High Court">Madras High Court</option>
              <option value="Calcutta High Court">Calcutta High Court</option>
            </select>
          </div>
        </div>
      )}
    </form>
  );
}
