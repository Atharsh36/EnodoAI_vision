import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { MainLayout } from './layouts/MainLayout';
import { DashboardPage } from './pages/DashboardPage';
import { ImageAnalysisPage } from './pages/ImageAnalysisPage';
import { LiveAnalysisPage } from './pages/LiveAnalysisPage';
import { VideoAnalysisPage } from './pages/VideoAnalysisPage';
import { DetectionResultsPage } from './pages/DetectionResultsPage';
import { ExplainabilityPage } from './pages/ExplainabilityPage';
import { ReportsPage } from './pages/ReportsPage';
import { HistoryPage } from './pages/HistoryPage';
import { ModelInfoPage } from './pages/ModelInfoPage';
import { SettingsPage } from './pages/SettingsPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<DashboardPage />} />
          <Route path="live" element={<LiveAnalysisPage />} />
          <Route path="image-analysis" element={<ImageAnalysisPage />} />
          <Route path="video-analysis" element={<VideoAnalysisPage />} />
          <Route path="detections" element={<DetectionResultsPage />} />
          <Route path="explainability" element={<ExplainabilityPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="model-info" element={<ModelInfoPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};
