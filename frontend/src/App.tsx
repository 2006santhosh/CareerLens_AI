import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { AppShell, ProtectedRoute, RequireAuthOnly } from './components/AppShell';

import Login from './pages/Login';
import Register from './pages/Register';
import Onboarding from './pages/Onboarding';
import Dashboard from './pages/Dashboard';
import Profile from './pages/Profile';
import Skills from './pages/Skills';
import Careers from './pages/Careers';
import CareerDetail from './pages/CareerDetail';
import GapAnalysis from './pages/GapAnalysis';
import Roadmap from './pages/Roadmap';
import Assessments from './pages/Assessments';
import AssessmentDetail from './pages/AssessmentDetail';
import PracticalAssessmentDetail from './pages/PracticalAssessmentDetail';
import Evidence from './pages/Evidence';
import Analytics from './pages/Analytics';
import Simulator from './pages/Simulator';
import JobMatcher from './pages/JobMatcher';
import Placement from './pages/Placement';
import Settings from './pages/Settings';

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route element={<RequireAuthOnly />}>
            <Route path="/onboarding" element={<Onboarding />} />
          </Route>

          <Route element={<ProtectedRoute />}>
            <Route element={<AppShell />}>
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/profile" element={<Profile />} />
              <Route path="/skills" element={<Skills />} />
              <Route path="/careers" element={<Careers />} />
              <Route path="/careers/:id" element={<CareerDetail />} />
              <Route path="/gap-analysis" element={<GapAnalysis />} />
              <Route path="/roadmap" element={<Roadmap />} />
              <Route path="/assessments" element={<Assessments />} />
              <Route path="/assessments/knowledge/:id" element={<AssessmentDetail />} />
              <Route path="/assessments/practical/:id" element={<PracticalAssessmentDetail />} />
              <Route path="/evidence" element={<Evidence />} />
              <Route path="/simulator" element={<Simulator />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/job-matcher" element={<JobMatcher />} />
              <Route path="/placement" element={<Placement />} />
              <Route path="/settings" element={<Settings />} />
            </Route>
          </Route>

          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}
