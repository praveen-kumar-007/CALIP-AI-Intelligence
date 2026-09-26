import React from 'react';
import { useApp } from '../../context/AppContext';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

export function ToastContainer() {
  const { toasts, removeToast } = useApp();

  if (!toasts || toasts.length === 0) return null;

  return (
    <div style={{
      position: 'fixed',
      bottom: '24px',
      right: '24px',
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column',
      gap: '10px',
      maxWidth: '400px',
    }}>
      {toasts.map((toast) => {
        const isSuccess = toast.type === 'success';
        const isError = toast.type === 'error';
        const isWarning = toast.type === 'warning';

        const borderColor = isSuccess ? 'rgba(16, 185, 129, 0.4)' : isError ? 'rgba(239, 68, 68, 0.4)' : 'rgba(99, 102, 241, 0.4)';
        const bgIconColor = isSuccess ? '#10b981' : isError ? '#ef4444' : '#6366f1';

        return (
          <div
            key={toast.id}
            className="animate-fade-in"
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '12px',
              padding: '12px 16px',
              background: '#0f172a',
              border: `1px solid ${borderColor}`,
              borderRadius: '10px',
              boxShadow: '0 8px 24px rgba(0, 0, 0, 0.6)',
              color: '#f8fafc',
              fontSize: '0.88rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              {isSuccess ? <CheckCircle2 size={18} color={bgIconColor} /> :
               isError ? <AlertCircle size={18} color={bgIconColor} /> :
               <Info size={18} color={bgIconColor} />}
              <span>{toast.message}</span>
            </div>
            <button
              onClick={() => removeToast(toast.id)}
              style={{ color: '#94a3b8', display: 'flex', alignItems: 'center' }}
            >
              <X size={16} />
            </button>
          </div>
        );
      })}
    </div>
  );
}
