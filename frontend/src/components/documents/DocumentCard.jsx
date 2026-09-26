import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Download, ExternalLink, Hash, Eye, Sparkles } from 'lucide-react';
import { StatusBadge } from '../common/StatusBadge';

export function DocumentCard({ doc }) {
  if (!doc) return null;

  return (
    <div className="glass-card glass-card-interactive" style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '10px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '32px',
            height: '32px',
            borderRadius: '8px',
            background: 'rgba(6, 182, 212, 0.12)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#06b6d4',
          }}>
            <FileText size={18} />
          </div>
          <div>
            <span style={{ fontSize: '0.72rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>
              {doc.document_type || 'Legal Order'}
            </span>
            <div style={{ fontSize: '0.8rem', color: '#94a3b8' }}>
              {doc.court || 'Court Record'}
            </div>
          </div>
        </div>
        <StatusBadge status={doc.ocr_status || 'EXTRACTED'} />
      </div>

      <h4 style={{ fontSize: '0.98rem', fontWeight: 700, color: '#f8fafc', lineHeight: 1.4 }}>
        <Link to={`/documents/${encodeURIComponent(doc.id)}`} style={{ color: 'inherit' }}>
          {doc.title || `Document ${doc.id}`}
        </Link>
      </h4>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', fontSize: '0.78rem', color: '#94a3b8' }}>
        <span>{doc.page_count ? `${doc.page_count} Pages` : '1 Page'}</span>
        <span>&bull;</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '4px', fontFamily: 'var(--font-mono)' }}>
          <Hash size={12} />
          {doc.file_hash ? `${doc.file_hash.substring(0, 10)}...` : 'Verified SHA-256'}
        </span>
      </div>

      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingTop: '10px',
        borderTop: '1px solid rgba(255, 255, 255, 0.06)',
        marginTop: 'auto',
      }}>
        <Link
          to={`/documents/${encodeURIComponent(doc.id)}`}
          className="btn btn-secondary btn-sm"
          style={{ gap: '6px' }}
        >
          <Eye size={13} />
          <span>View / OCR</span>
        </Link>

        {doc.original_pdf_url && (
          <a
            href={doc.original_pdf_url}
            target="_blank"
            rel="noreferrer"
            className="btn btn-secondary btn-sm"
            style={{ gap: '4px', color: '#06b6d4' }}
            title="Download Original PDF"
          >
            <Download size={13} />
            <span>PDF</span>
          </a>
        )}
      </div>
    </div>
  );
}
