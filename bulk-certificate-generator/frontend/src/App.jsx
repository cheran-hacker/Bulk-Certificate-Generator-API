import { Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import CreateJob from './pages/CreateJob';
import JobDetails from './pages/JobDetails';
import Jobs from './pages/Jobs';
import Certificates from './pages/Certificates';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';

export default function App() {
  return (
    <>
      <Toaster position="top-right" toastOptions={{
        style: {
          background: 'var(--bg-surface)',
          color: 'var(--text-main)',
          border: '1px solid var(--border)'
        }
      }} />
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="jobs" element={<Jobs />} />
          <Route path="jobs/create" element={<CreateJob />} />
          <Route path="jobs/:jobId" element={<JobDetails />} />
          <Route path="certificates" element={<Certificates />} />
          <Route path="settings" element={<Settings />} />
          <Route path="docs" element={<Navigate to={() => { window.open(import.meta.env.VITE_API_BASE_URL + '/docs', '_blank'); return null; }} />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </>
  );
}