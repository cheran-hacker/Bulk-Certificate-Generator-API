import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())

job_details = """
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { jobsApi } from '../api/jobs';
import { FileText, CheckCircle2, XCircle, Clock, AlertTriangle, Download, Eye, X, Archive } from 'lucide-react';
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
        <div className="d-flex gap-3 align-items-center">
          {isDone && job.success_count > 0 && (
            <a href={`${import.meta.env.VITE_API_BASE_URL}/api/v1/jobs/${job.job_id}/download-zip`} 
               className="btn btn-secondary-custom shadow-sm text-primary d-flex align-items-center fw-semibold">
              <Archive size={18} className="me-2" /> Download All (ZIP)
            </a>
          )}
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

create_file("frontend/src/pages/JobDetails.jsx", job_details)
print("upgraded 6")
