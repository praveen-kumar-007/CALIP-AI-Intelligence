import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import { MainLayout } from './components/layout/MainLayout';

// Page Imports
import { HomePage } from './pages/HomePage';
import { SearchPage } from './pages/SearchPage';
import { CasesPage } from './pages/CasesPage';
import { CaseDetailPage } from './pages/CaseDetailPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { DocumentDetailPage } from './pages/DocumentDetailPage';
import { AtomsPage } from './pages/AtomsPage';
import { AtomDetailPage } from './pages/AtomDetailPage';
import { AIResearchPage } from './pages/AIResearchPage';
import { CourtsPage } from './pages/CourtsPage';
import { LongtailPage } from './pages/LongtailPage';
import { AdminDashboardPage } from './pages/AdminDashboardPage';
import { ReviewQueuePage } from './pages/ReviewQueuePage';
import { AboutPage } from './pages/AboutPage';

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainLayout />}>
            <Route index element={<HomePage />} />
            <Route path="search" element={<SearchPage />} />
            <Route path="cases" element={<CasesPage />} />
            <Route path="cases/:id" element={<CaseDetailPage />} />
            <Route path="documents" element={<DocumentsPage />} />
            <Route path="documents/:id" element={<DocumentDetailPage />} />
            <Route path="atoms" element={<AtomsPage />} />
            <Route path="atoms/:id" element={<AtomDetailPage />} />
            <Route path="ai-research" element={<AIResearchPage />} />
            <Route path="courts" element={<CourtsPage />} />
            <Route path="longtail" element={<LongtailPage />} />
            <Route path="admin" element={<AdminDashboardPage />} />
            <Route path="admin/dashboard" element={<Navigate to="/admin" replace />} />
            <Route path="admin/review-queue" element={<ReviewQueuePage />} />
            <Route path="about" element={<AboutPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </AppProvider>
  );
}
