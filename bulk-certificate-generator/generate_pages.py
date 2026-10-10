import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())

app_jsx = """
import { Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import CreateJob from './pages/CreateJob';
import JobDetails from './pages/JobDetails';
import Certificates from './pages/Certificates';
import NotFound from './pages/NotFound';

export default function App() {
  return (
    <>
      <Toaster position="top-right" />
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="jobs" element={<Navigate to="/" replace />} />
          <Route path="jobs/create" element={<CreateJob />} />
          <Route path="jobs/:jobId" element={<JobDetails />} />
          <Route path="certificates" element={<Certificates />} />
          <Route path="docs" element={<Navigate to={() => { window.open(import.meta.env.VITE_API_BASE_URL + '/docs', '_blank'); return null; }} />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </>
  );
}
"""

main_jsx = """
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import 'bootstrap/dist/css/bootstrap.min.css'
import './styles/global.css'
import { BrowserRouter } from 'react-router-dom'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
"""

index_html = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>CertiFlow - Bulk Certificate Generator</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""

dashboard = """
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Plus, Activity, FileCheck, AlertCircle } from 'lucide-react';
import { jobsApi } from '../api/jobs';

export default function Dashboard() {
  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 className="fw-bold mb-1">Certificate Generation Dashboard</h2>
          <p className="text-muted mb-0">Monitor and manage your bulk certificate generation jobs.</p>
        </div>
        <Link to="/jobs/create" className="btn btn-primary-custom d-flex align-items-center">
          <Plus size={20} className="me-2" /> Create Certificate Job
        </Link>
      </div>
      
      <div className="row g-4 mb-4">
        <div className="col-md-3">
          <div className="card-custom p-4 h-100">
            <div className="d-flex align-items-center mb-3">
              <div className="p-2 bg-primary bg-opacity-10 rounded text-primary me-3">
                <Activity size={24} />
              </div>
              <h6 className="mb-0 text-muted">System Status</h6>
            </div>
            <h3 className="fw-bold mb-0">Ready</h3>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card-custom p-4 h-100">
            <div className="d-flex align-items-center mb-3">
              <div className="p-2 bg-success bg-opacity-10 rounded text-success me-3">
                <FileCheck size={24} />
              </div>
              <h6 className="mb-0 text-muted">API Connection</h6>
            </div>
            <h3 className="fw-bold mb-0 text-success">Healthy</h3>
          </div>
        </div>
      </div>
      
      <div className="card-custom overflow-hidden">
        <div className="p-4 border-bottom" style={{ borderColor: 'var(--border-color)' }}>
          <h5 className="fw-bold mb-0">Quick Actions</h5>
        </div>
        <div className="p-4">
          <div className="row g-4">
            <div className="col-md-4">
              <Link to="/jobs/create" className="text-decoration-none">
                <div className="p-4 border rounded text-center custom-action-card" style={{ borderColor: 'var(--border-color)' }}>
                  <Plus size={32} className="text-primary mb-3" />
                  <h6 className="fw-bold" style={{ color: 'var(--text-primary)' }}>New Job</h6>
                  <p className="small text-muted mb-0">Upload recipients and generate</p>
                </div>
              </Link>
            </div>
            <div className="col-md-4">
              <a href={import.meta.env.VITE_API_BASE_URL + '/docs'} target="_blank" rel="noreferrer" className="text-decoration-none">
                <div className="p-4 border rounded text-center custom-action-card" style={{ borderColor: 'var(--border-color)' }}>
                  <AlertCircle size={32} className="text-info mb-3" />
                  <h6 className="fw-bold" style={{ color: 'var(--text-primary)' }}>API Docs</h6>
                  <p className="small text-muted mb-0">View Swagger OpenAPI specs</p>
                </div>
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
"""

not_found = """
import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="d-flex flex-column align-items-center justify-content-center h-100 py-5">
      <h1 className="display-1 fw-bold text-primary mb-3">404</h1>
      <h3 className="fw-bold mb-2">Page Not Found</h3>
      <p className="text-muted mb-4">The page you're looking for doesn't exist.</p>
      <Link to="/" className="btn btn-primary-custom">Go to Dashboard</Link>
    </div>
  );
}
"""

create_file("frontend/src/App.jsx", app_jsx)
create_file("frontend/src/main.jsx", main_jsx)
create_file("frontend/index.html", index_html)
create_file("frontend/src/pages/Dashboard.jsx", dashboard)
create_file("frontend/src/pages/NotFound.jsx", not_found)
print("Generated main files and dashboard")
