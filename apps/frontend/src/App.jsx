import React from "react"
import { BrowserRouter, Routes, Route, useLocation, Navigate } from "react-router-dom"
import Dashboard from "@/pages/Dashboard"
import Login from "@/pages/Login"
import Settings from "@/pages/Settings"
import InfrastructureGraph from "@/pages/InfrastructureGraph"
import DriftDetection from "@/pages/DriftDetection"
import SecretScanner from "@/pages/SecretScanner"
import ComplianceReports from "@/pages/ComplianceReports"
import ScansHistory from "@/pages/ScansHistory"
import Placeholder from "@/pages/Placeholder"

// Protected Route Component
function ProtectedRoute({ children }) {
  const token = localStorage.getItem('access_token');

  if (!token) {
    // For demo purposes, we might allow bypassing login if we want to show the UI
    // But strictly speaking: return <Navigate to="/login" replace />;
    // Let's keep it strict but ensure Login sets the token.
    return <Navigate to="/login" replace />;
  }

  // Layout is now handled by individual pages via Shell component
  return children;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        {/* Protected Routes */}
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/infrastructure" element={
          <ProtectedRoute>
            <InfrastructureGraph />
          </ProtectedRoute>
        } />
        <Route path="/drift" element={
          <ProtectedRoute>
            <DriftDetection />
          </ProtectedRoute>
        } />
        <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />

        <Route path="/projects" element={<ProtectedRoute><Placeholder title="Projetos" /></ProtectedRoute>} />
        <Route path="/scans" element={
          <ProtectedRoute>
            <ScansHistory />
          </ProtectedRoute>
        } />
        <Route path="/compliance" element={
          <ProtectedRoute>
            <ComplianceReports />
          </ProtectedRoute>
        } />
        <Route path="/secrets" element={
          <ProtectedRoute>
            <SecretScanner />
          </ProtectedRoute>
        } />
        <Route path="/reports" element={<ProtectedRoute><ComplianceReports /></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
