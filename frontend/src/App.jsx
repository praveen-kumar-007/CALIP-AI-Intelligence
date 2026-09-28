import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import { MainLayout } from './components/layout/MainLayout';

// Core 24-Atom Platform Pages
import { HomePage } from './pages/HomePage';
import { AtomsPage } from './pages/AtomsPage';
import { AtomDetailPage } from './pages/AtomDetailPage';
import { AIResearchPage } from './pages/AIResearchPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { DocumentDetailPage } from './pages/DocumentDetailPage';
import { SearchPage } from './pages/SearchPage';
import { AdminDashboardPage } from './pages/AdminDashboardPage';
import { ReviewQueuePage } from './pages/ReviewQueuePage';
import { DatabaseHierarchyPage } from './pages/DatabaseHierarchyPage';

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            {/* Primary 24 Pilot Atoms Application Routes */}
            <Route index element={<HomePage />} />
            <Route path="atoms" element={<AtomsPage />} />
            <Route path="atoms/:id" element={<AtomDetailPage />} />
            <Route path="ai-research" element={<AIResearchPage />} />
            <Route path="documents" element={<DocumentsPage />} />
            <Route path="documents/:id" element={<DocumentDetailPage />} />
            <Route path="database-hierarchy" element={<DatabaseHierarchyPage />} />
            <Route path="search" element={<SearchPage />} />
            <Route path="admin" element={<AdminDashboardPage />} />
            <Route path="admin/dashboard" element={<Navigate to="/admin" replace />} />
            <Route path="admin/review-queue" element={<ReviewQueuePage />} />

            {/* Aliases for Database Structure & Hierarchy */}
            <Route path="hierarchy" element={<Navigate to="/database-hierarchy" replace />} />
            <Route path="db-structure" element={<Navigate to="/database-hierarchy" replace />} />
            <Route path="database-structure" element={<Navigate to="/database-hierarchy" replace />} />

            {/* Seamless Redirects for Legacy / Unused Routes */}
            <Route path="cases" element={<Navigate to="/atoms" replace />} />
            <Route path="cases/:id" element={<Navigate to="/atoms" replace />} />
            <Route path="longtail" element={<Navigate to="/atoms" replace />} />
            <Route path="courts" element={<Navigate to="/atoms" replace />} />
            <Route path="judgments" element={<Navigate to="/documents" replace />} />
            <Route path="orders" element={<Navigate to="/documents" replace />} />
            <Route path="about" element={<Navigate to="/atoms" replace />} />

            {/* Catch-all fallback */}
            <Route path="*" element={<Navigate to="/atoms" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}
