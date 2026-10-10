import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())

api_certificates = """
import { apiClient } from './client';

export const certificatesApi = {
  getCertificates: async (page = 1, pageSize = 50) => {
    const response = await apiClient.get(`/api/v1/certificates?page=${page}&page_size=${pageSize}`);
    return response.data;
  },
  getCertificate: async (certId) => {
    const response = await apiClient.get(`/api/v1/certificates/${certId}`);
    return response.data;
  },
  downloadCertificate: async (certId) => {
    const response = await apiClient.get(`/api/v1/certificates/${certId}/download`, {
      responseType: 'blob',
    });
    return response.data;
  },
};
"""

certificates_page = """
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FileText, Search, Download, Eye, X } from 'lucide-react';
import { certificatesApi } from '../api/certificates';
import toast from 'react-hot-toast';

export default function Certificates() {
  const [certs, setCerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [previewUrl, setPreviewUrl] = useState(null);

  useEffect(() => {
    const fetchCerts = async () => {
      try {
        const res = await certificatesApi.getCertificates(1, 100);
        setCerts(res.items || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchCerts();
  }, []);

  const handlePreview = (certId) => {
    setPreviewUrl(`${import.meta.env.VITE_API_BASE_URL}/api/v1/certificates/${certId}/download`);
  };

  const filtered = certs.filter(c => 
    c.recipient_name.toLowerCase().includes(search.toLowerCase()) || 
    c.recipient_email.toLowerCase().includes(search.toLowerCase()) ||
    c.certificate_code.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="container-fluid py-2">
      <div className="mb-4">
        <h2 className="fw-bold mb-1">Certificates Library</h2>
        <p className="text-muted-custom mb-0">Search and view all generated certificates.</p>
      </div>

      <div className="surface overflow-hidden mb-5">
        <div className="p-4 border-bottom" style={{ borderColor: 'var(--border)' }}>
          <div className="position-relative" style={{ width: '100%', maxWidth: 400 }}>
            <Search size={18} className="position-absolute text-muted-custom" style={{ top: 11, left: 12 }} />
            <input type="text" className="form-control-custom ps-5" placeholder="Search by name, email, or code..."
                   value={search} onChange={e => setSearch(e.target.value)} />
          </div>
        </div>

        <div className="table-container">
          <table className="table-custom">
            <thead>
              <tr>
                <th>Code</th>
                <th>Recipient Name</th>
                <th>Email Address</th>
                <th>Status</th>
                <th className="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="5" className="text-center py-5">
                    <span className="spinner-border text-primary opacity-50" />
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan="5" className="text-center py-5 text-muted-custom">
                     <FileText size={48} className="mb-3 opacity-50 mx-auto" />
                     <p className="mb-0">No certificates found.</p>
                  </td>
                </tr>
              ) : (
                filtered.map(c => (
                  <tr key={c.id}>
                    <td className="font-monospace text-muted-custom small">{c.certificate_code}</td>
                    <td className="fw-medium">{c.recipient_name}</td>
                    <td className="text-muted-custom">{c.recipient_email}</td>
                    <td>
                      {c.status === 'COMPLETED' ? <span className="badge-custom badge-success">Generated</span> :
                       <span className="badge-custom badge-danger">Failed</span>}
                    </td>
                    <td className="text-end">
                      {c.status === 'COMPLETED' && (
                        <div className="d-flex justify-content-end gap-2">
                          <button onClick={() => handlePreview(c.id)} className="btn btn-sm btn-secondary-custom p-2" title="Preview PDF">
                            <Eye size={16} />
                          </button>
                          <a href={`${import.meta.env.VITE_API_BASE_URL}/api/v1/certificates/${c.id}/download`} 
                             target="_blank" rel="noreferrer"
                             className="btn btn-sm btn-primary-custom p-2" title="Download PDF">
                            <Download size={16} />
                          </a>
                        </div>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <AnimatePresence>
        {previewUrl && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center"
            style={{ backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1050, padding: 20 }}>
            
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
              className="surface overflow-hidden d-flex flex-column"
              style={{ width: '100%', maxWidth: 900, height: '90vh' }}>
              
              <div className="p-3 border-bottom d-flex justify-content-between align-items-center bg-light" style={{ borderColor: 'var(--border)' }}>
                <h5 className="mb-0 fw-bold d-flex align-items-center"><FileText size={20} className="me-2 text-primary"/> Certificate Preview</h5>
                <button className="btn btn-link text-muted-custom p-0" onClick={() => setPreviewUrl(null)}>
                  <X size={24} />
                </button>
              </div>
              
              <div className="flex-grow-1 bg-secondary bg-opacity-10">
                <iframe src={previewUrl} className="w-100 h-100 border-0" title="PDF Preview"></iframe>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
"""

sidebar = """
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, FilePlus2, Layers, BookOpen, Settings, PanelLeftClose, PanelLeftOpen, FileText } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Sidebar({ isOpen, toggle }) {
  const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/jobs', icon: Layers, label: 'Jobs' },
    { to: '/jobs/create', icon: FilePlus2, label: 'Create Job' },
    { to: '/certificates', icon: FileText, label: 'Certificates' }
  ];
  
  const bottomItems = [
    { to: '/settings', icon: Settings, label: 'Settings' }
  ];

  const extItems = [
    { href: import.meta.env.VITE_API_BASE_URL + '/docs', icon: BookOpen, label: 'API Documentation' }
  ];

  return (
    <motion.aside 
      initial={false}
      animate={{ width: isOpen ? 260 : 80 }}
      className="d-flex flex-column flex-shrink-0" 
      style={{ 
        backgroundColor: 'var(--bg-surface)', 
        borderRight: '1px solid var(--border)',
        height: '100vh',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        overflowX: 'hidden'
      }}>
      
      <div className="d-flex align-items-center mb-4 px-3 mt-4" style={{ height: 40 }}>
        {isOpen ? (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="d-flex align-items-center gap-2 w-100">
            <div className="bg-primary text-white rounded p-1 d-flex align-items-center justify-content-center shadow-sm" style={{ width: 32, height: 32 }}>
               <span className="fw-bold fs-5" style={{ lineHeight: 1 }}>C</span>
            </div>
            <span className="fs-5 fw-bold" style={{ color: 'var(--text-main)', letterSpacing: '-0.5px' }}>CertiFlow</span>
          </motion.div>
        ) : (
          <div className="w-100 d-flex justify-content-center">
            <div className="bg-primary text-white rounded p-1 d-flex align-items-center justify-content-center shadow-sm" style={{ width: 32, height: 32 }}>
               <span className="fw-bold fs-5" style={{ lineHeight: 1 }}>C</span>
            </div>
          </div>
        )}
      </div>
      
      <div className="px-3 mb-2 mt-2">
        <span className="text-uppercase fw-semibold" style={{ fontSize: '0.65rem', color: 'var(--text-muted)', display: isOpen ? 'block' : 'none' }}>Main Menu</span>
      </div>
      
      <ul className="nav nav-pills flex-column mb-auto px-2 gap-1">
        {navItems.map((item) => (
          <li className="nav-item" key={item.to}>
            <NavLink 
              to={item.to} 
              className={({ isActive }) => `nav-link d-flex align-items-center transition-all`}
              style={({ isActive }) => ({
                backgroundColor: isActive ? 'var(--primary)' : 'transparent',
                color: isActive ? '#fff' : 'var(--text-muted)',
                justifyContent: isOpen ? 'flex-start' : 'center',
                padding: '10px 12px',
                borderRadius: '8px',
                fontWeight: isActive ? 500 : 400
              })}
            >
              <item.icon size={20} className={isOpen ? "me-3" : ""} style={{ flexShrink: 0 }} />
              {isOpen && <span style={{ whiteSpace: 'nowrap' }}>{item.label}</span>}
            </NavLink>
          </li>
        ))}
      </ul>
      
      <div className="px-3 mb-2 mt-4">
        <span className="text-uppercase fw-semibold" style={{ fontSize: '0.65rem', color: 'var(--text-muted)', display: isOpen ? 'block' : 'none' }}>Resources</span>
      </div>
      <ul className="nav nav-pills flex-column px-2 gap-1 mb-4">
        {extItems.map((item) => (
          <li className="nav-item" key={item.label}>
            <a 
              href={item.href} target="_blank" rel="noreferrer"
              className="nav-link d-flex align-items-center"
              style={{
                color: 'var(--text-muted)',
                justifyContent: isOpen ? 'flex-start' : 'center',
                padding: '10px 12px',
                borderRadius: '8px',
                fontWeight: 400
              }}
            >
              <item.icon size={20} className={isOpen ? "me-3" : ""} style={{ flexShrink: 0 }} />
              {isOpen && <span style={{ whiteSpace: 'nowrap' }}>{item.label}</span>}
            </a>
          </li>
        ))}
        {bottomItems.map((item) => (
          <li className="nav-item" key={item.to}>
            <NavLink 
              to={item.to} 
              className={({ isActive }) => `nav-link d-flex align-items-center transition-all`}
              style={({ isActive }) => ({
                backgroundColor: isActive ? 'var(--primary)' : 'transparent',
                color: isActive ? '#fff' : 'var(--text-muted)',
                justifyContent: isOpen ? 'flex-start' : 'center',
                padding: '10px 12px',
                borderRadius: '8px',
                fontWeight: isActive ? 500 : 400
              })}
            >
              <item.icon size={20} className={isOpen ? "me-3" : ""} style={{ flexShrink: 0 }} />
              {isOpen && <span style={{ whiteSpace: 'nowrap' }}>{item.label}</span>}
            </NavLink>
          </li>
        ))}
      </ul>
      
      <div className="p-3 border-top" style={{ borderColor: 'var(--border)' }}>
        <button className="btn btn-link text-decoration-none d-flex align-items-center w-100 p-2" 
                onClick={toggle}
                style={{ color: 'var(--text-muted)', justifyContent: isOpen ? 'flex-start' : 'center', borderRadius: 8 }}>
          {isOpen ? <PanelLeftClose size={20} className="me-2" /> : <PanelLeftOpen size={20} />}
          {isOpen && <span>Collapse Sidebar</span>}
        </button>
      </div>
    </motion.aside>
  );
}
"""

app_jsx = """
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
"""

job_details = """
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { jobsApi } from '../api/jobs';
import { FileText, CheckCircle2, XCircle, Clock, AlertTriangle, Download, Eye, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function JobDetails() {
  const { jobId } = useParams();
  const [job, setJob] = useState(null);
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [previewUrl, setPreviewUrl] = useState(null);

  useEffect(() => {
    let interval;
    const fetchJob = async () => {
      try {
        const res = await jobsApi.getJob(jobId);
        setJob(res.data);
        
        if (res.data.status === 'COMPLETED' || res.data.status === 'COMPLETED_WITH_ERRORS' || res.data.status === 'FAILED') {
          clearInterval(interval);
          const certRes = await jobsApi.getJobCertificates(jobId);
          setCertificates(certRes.items || []);
        }
      } catch (err) {
        clearInterval(interval);
      } finally {
        setLoading(false);
      }
    };

    fetchJob();
    interval = setInterval(fetchJob, 1500);
    return () => clearInterval(interval);
  }, [jobId]);

  const handlePreview = (certId) => {
    setPreviewUrl(`${import.meta.env.VITE_API_BASE_URL}/api/v1/certificates/${certId}/download`);
  };

  if (loading) return (
    <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '60vh' }}>
      <span className="spinner-border text-primary" style={{ width: '3rem', height: '3rem' }} />
    </div>
  );
  
  if (!job) return <div className="p-5 text-center text-muted-custom">Job not found.</div>;

  const isDone = ['COMPLETED', 'COMPLETED_WITH_ERRORS', 'FAILED'].includes(job.status);
  const progressPercent = Math.round(job.progress_percentage);

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="container-fluid py-2">
      <div className="mb-5 d-flex justify-content-between align-items-end">
        <div>
          <h2 className="fw-bold mb-1">Job Processing</h2>
          <p className="text-muted-custom mb-0 font-monospace small">ID: {job.job_id}</p>
        </div>
        <div>
          {job.status === 'COMPLETED' ? <span className="badge-custom badge-success fs-6"><CheckCircle2 size={16}/> Completed</span> :
           job.status === 'COMPLETED_WITH_ERRORS' ? <span className="badge-custom badge-warning fs-6"><AlertTriangle size={16}/> Completed with Errors</span> :
           job.status === 'FAILED' ? <span className="badge-custom badge-danger fs-6"><XCircle size={16}/> Failed</span> :
           <span className="badge-custom badge-info fs-6"><Clock size={16} className="animate-pulse-subtle"/> Processing</span>}
        </div>
      </div>

      <div className="surface p-4 p-md-5 mb-5 position-relative overflow-hidden">
        {!isDone && (
          <div className="position-absolute top-0 start-0 w-100 h-100 pointer-events-none" 
               style={{ background: 'radial-gradient(circle at right top, rgba(79, 70, 229, 0.05), transparent 40%)', zIndex: 0 }} />
        )}
        
        <div className="position-relative z-1">
          <div className="d-flex justify-content-between align-items-end mb-3">
            <div>
              <h3 className="fw-bold mb-0" style={{ fontSize: '2.5rem' }}>{progressPercent}%</h3>
              <p className="text-muted-custom mb-0">{job.success_count + job.failed_count} of {job.total_recipients} recipients processed</p>
            </div>
            {!isDone && <span className="text-primary fw-medium animate-pulse-subtle">Generating PDFs...</span>}
          </div>
          
          <div className="progress mb-4 rounded-pill overflow-hidden" style={{ height: '12px', backgroundColor: 'var(--bg-app)' }}>
            <motion.div 
              className="progress-bar bg-primary"
              initial={{ width: 0 }}
              animate={{ width: `${progressPercent}%` }}
              transition={{ ease: "easeOut", duration: 0.5 }}
            />
          </div>
          
          <div className="row g-4 mt-2">
            <div className="col-md-4">
              <div className="d-flex align-items-center p-3 rounded" style={{ backgroundColor: 'var(--success-bg)' }}>
                <CheckCircle2 size={24} className="me-3" style={{ color: 'var(--success-text)' }} />
                <div>
                  <h4 className="fw-bold mb-0" style={{ color: 'var(--success-text)' }}>{job.success_count}</h4>
                  <span className="small fw-medium" style={{ color: 'var(--success-text)', opacity: 0.8 }}>Successful</span>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="d-flex align-items-center p-3 rounded" style={{ backgroundColor: 'var(--danger-bg)' }}>
                <XCircle size={24} className="me-3" style={{ color: 'var(--danger-text)' }} />
                <div>
                  <h4 className="fw-bold mb-0" style={{ color: 'var(--danger-text)' }}>{job.failed_count}</h4>
                  <span className="small fw-medium" style={{ color: 'var(--danger-text)', opacity: 0.8 }}>Failed</span>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="d-flex align-items-center p-3 rounded" style={{ backgroundColor: 'var(--bg-app)', border: '1px solid var(--border)' }}>
                <Clock size={24} className="me-3 text-muted-custom" />
                <div>
                  <h4 className="fw-bold mb-0">{job.pending_count}</h4>
                  <span className="small fw-medium text-muted-custom">Remaining</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="d-flex justify-content-between align-items-center mb-4">
        <h4 className="fw-bold mb-0">Generated Certificates</h4>
      </div>

      <div className="surface overflow-hidden">
        {!isDone ? (
          <div className="p-5 text-center text-muted-custom">
            <Clock size={40} className="mb-3 opacity-50 animate-pulse-subtle mx-auto" />
            <p className="mb-0">Certificates will appear here once the job finishes processing.</p>
          </div>
        ) : certificates.length === 0 ? (
          <div className="p-5 text-center text-muted-custom">
            <p className="mb-0">No certificates generated.</p>
          </div>
        ) : (
          <div className="table-container">
            <table className="table-custom">
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Recipient Name</th>
                  <th>Status</th>
                  <th>Error Information</th>
                  <th className="text-end">Action</th>
                </tr>
              </thead>
              <tbody>
                {certificates.map(c => (
                  <tr key={c.id}>
                    <td className="font-monospace text-muted-custom small">{c.certificate_code}</td>
                    <td className="fw-medium">{c.recipient_name}</td>
                    <td>
                      {c.status === 'COMPLETED' ? <span className="badge-custom badge-success">Success</span> :
                       <span className="badge-custom badge-danger">Failed</span>}
                    </td>
                    <td className="text-danger small">{c.error_message || '-'}</td>
                    <td className="text-end">
                      {c.status === 'COMPLETED' && (
                        <div className="d-flex justify-content-end gap-2">
                          <button onClick={() => handlePreview(c.id)} className="btn btn-sm btn-secondary-custom p-2" title="Preview PDF">
                            <Eye size={16} />
                          </button>
                          <a href={`${import.meta.env.VITE_API_BASE_URL}/api/v1/certificates/${c.id}/download`} 
                             target="_blank" rel="noreferrer"
                             className="btn btn-sm btn-primary-custom p-2" title="Download PDF">
                            <Download size={16} />
                          </a>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <AnimatePresence>
        {previewUrl && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center"
            style={{ backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1050, padding: 20 }}>
            
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
              className="surface overflow-hidden d-flex flex-column"
              style={{ width: '100%', maxWidth: 900, height: '90vh' }}>
              
              <div className="p-3 border-bottom d-flex justify-content-between align-items-center bg-light" style={{ borderColor: 'var(--border)' }}>
                <h5 className="mb-0 fw-bold d-flex align-items-center"><FileText size={20} className="me-2 text-primary"/> Certificate Preview</h5>
                <button className="btn btn-link text-muted-custom p-0" onClick={() => setPreviewUrl(null)}>
                  <X size={24} />
                </button>
              </div>
              
              <div className="flex-grow-1 bg-secondary bg-opacity-10">
                <iframe src={previewUrl} className="w-100 h-100 border-0" title="PDF Preview"></iframe>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
"""

create_file("frontend/src/api/certificates.js", api_certificates)
create_file("frontend/src/pages/Certificates.jsx", certificates_page)
create_file("frontend/src/components/Sidebar.jsx", sidebar)
create_file("frontend/src/App.jsx", app_jsx)
create_file("frontend/src/pages/JobDetails.jsx", job_details)
print("upgraded 5")
