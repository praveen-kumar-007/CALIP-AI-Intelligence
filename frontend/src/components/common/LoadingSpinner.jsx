import React from 'react';
import { Loader2 } from 'lucide-react';

export function LoadingSpinner({ text = 'Loading legal intelligence records...', size = 32 }) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '48px 24px',
      gap: '16px',
      color: '#94a3b8',
    }}>
      <Loader2
        size={size}
        color="#6366f1"
        style={{
          animation: 'spin 1s linear infinite',
        }}
      />
      <span style={{ fontSize: '0.92rem', fontWeight: 500 }}>{text}</span>
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="glass-card" style={{ opacity: 0.6, display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ height: '20px', width: '60%', background: '#334155', borderRadius: '4px' }} className="animate-pulse" />
      <div style={{ height: '14px', width: '40%', background: '#1e293b', borderRadius: '4px' }} className="animate-pulse" />
      <div style={{ height: '40px', width: '100%', background: '#1e293b', borderRadius: '4px', marginTop: '8px' }} className="animate-pulse" />
    </div>
  );
}
