import React from 'react';
import { CheckCircle, Clock, AlertTriangle, FileText, ShieldCheck } from 'lucide-react';

export function StatusBadge({ status, type = 'status' }) {
  if (!status) return null;

  const normalized = String(status).toUpperCase();

  if (normalized.includes('VERIFIED') || normalized === 'COMPLETED' || normalized === 'EXTRACTED' || normalized === 'DISPOSED') {
    return (
      <span className="badge badge-emerald">
        <CheckCircle size={12} />
        {status}
      </span>
    );
  }

  if (normalized.includes('PENDING') || normalized.includes('QUEUED') || normalized.includes('PROCESSING')) {
    return (
      <span className="badge badge-amber">
        <Clock size={12} />
        {status}
      </span>
    );
  }

  if (normalized.includes('FAIL') || normalized.includes('REJECTED') || normalized.includes('CONFLICT')) {
    return (
      <span className="badge badge-rose">
        <AlertTriangle size={12} />
        {status}
      </span>
    );
  }

  if (normalized.includes('HIGH COURT') || normalized.includes('SUPREME')) {
    return (
      <span className="badge badge-indigo">
        <ShieldCheck size={12} />
        {status}
      </span>
    );
  }

  return (
    <span className="badge badge-slate">
      <FileText size={12} />
      {status}
    </span>
  );
}
