import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())

create_job = """
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { jobsApi } from '../api/jobs';
import toast from 'react-hot-toast';
import { Trash2, Plus, Upload, CheckCircle, ChevronRight, FileUp, AlertTriangle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Papa from 'papaparse';

export default function CreateJob() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);
  
  const [formData, setFormData] = useState({
    certificate_title: 'Certificate of Excellence',
    event_name: '',
    organization_name: '',
    issue_date: new Date().toISOString().split('T')[0],
  });
  
  const [recipients, setRecipients] = useState([{ name: '', email: '' }]);

  const handleAddRecipient = () => setRecipients([...recipients, { name: '', email: '' }]);
  const handleRemoveRecipient = (index) => setRecipients(recipients.filter((_, i) => i !== index));
  const handleRecipientChange = (index, field, value) => {
    const newRecipients = [...recipients];
    newRecipients[index][field] = value;
    setRecipients(newRecipients);
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: function(results) {
        const parsed = results.data.map(row => ({
          name: row.name || row.Name || row.NAME || '',
          email: row.email || row.Email || row.EMAIL || ''
        })).filter(r => r.name || r.email);
        
        if (parsed.length > 0) {
          setRecipients(parsed);
          toast.success(`Loaded ${parsed.length} recipients from CSV`);
        } else {
          toast.error("Could not find 'name' or 'email' columns in CSV");
        }
      }
    });
  };

  const validRecipients = recipients.filter(r => r.name.trim() !== '' && r.email.trim() !== '' && r.email.includes('@'));
  const invalidCount = recipients.length - validRecipients.length;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (step === 1) return setStep(2);
    if (step === 2) return setStep(3);
    
    if (validRecipients.length === 0) {
      toast.error('Please add at least one valid recipient.');
      return;
    }

    try {
      setLoading(true);
      const res = await jobsApi.createJob({ ...formData, recipients: validRecipients });
      toast.success('Generation job queued successfully!');
      navigate(`/jobs/${res.data.job_id}`);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const anim = {
    initial: { opacity: 0, x: 20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 }
  };

  return (
    <div className="container-fluid py-2 max-w-4xl mx-auto" style={{ maxWidth: 900 }}>
      <div className="mb-5">
        <h2 className="fw-bold mb-1">Create Certificate Job</h2>
        <p className="text-muted-custom mb-0">Generate certificates in bulk using a standard template.</p>
      </div>

      <div className="d-flex mb-5 position-relative">
        <div className="progress position-absolute" style={{ top: '50%', transform: 'translateY(-50%)', left: 0, right: 0, height: 4, zIndex: 0, backgroundColor: 'var(--border)' }}>
          <div className="progress-bar bg-primary" style={{ width: step === 1 ? '0%' : step === 2 ? '50%' : '100%', transition: 'width 0.4s ease' }}></div>
        </div>
        {[1,2,3].map(s => (
          <div key={s} className="d-flex flex-column align-items-center position-relative z-1" style={{ flex: 1 }}>
            <div className={`rounded-circle d-flex align-items-center justify-content-center fw-bold transition-all`} 
                 style={{ 
                   width: 32, height: 32, 
                   backgroundColor: step >= s ? 'var(--primary)' : 'var(--bg-surface)', 
                   color: step >= s ? '#fff' : 'var(--text-muted)',
                   border: step >= s ? 'none' : '2px solid var(--border)'
                 }}>
              {step > s ? <CheckCircle size={18} /> : s}
            </div>
            <span className="small fw-medium mt-2" style={{ color: step >= s ? 'var(--text-main)' : 'var(--text-muted)' }}>
              {s === 1 ? 'Details' : s === 2 ? 'Recipients' : 'Review'}
            </span>
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="surface p-4 p-md-5">
        <AnimatePresence mode="wait">
          
          {step === 1 && (
            <motion.div key="step1" {...anim} transition={{ duration: 0.2 }}>
              <h5 className="fw-bold mb-4">Job Details</h5>
              <div className="row g-4">
                <div className="col-md-6">
                  <label className="form-label-custom">Certificate Title</label>
                  <input type="text" className="form-control-custom" required
                    value={formData.certificate_title} onChange={e => setFormData({...formData, certificate_title: e.target.value})} />
                </div>
                <div className="col-md-6">
                  <label className="form-label-custom">Event Name</label>
                  <input type="text" className="form-control-custom" required
                    value={formData.event_name} onChange={e => setFormData({...formData, event_name: e.target.value})} />
                </div>
                <div className="col-md-6">
                  <label className="form-label-custom">Organization Name</label>
                  <input type="text" className="form-control-custom" required
                    value={formData.organization_name} onChange={e => setFormData({...formData, organization_name: e.target.value})} />
                </div>
                <div className="col-md-6">
                  <label className="form-label-custom">Issue Date</label>
                  <input type="date" className="form-control-custom" required
                    value={formData.issue_date} onChange={e => setFormData({...formData, issue_date: e.target.value})} />
                </div>
              </div>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div key="step2" {...anim} transition={{ duration: 0.2 }}>
              <div className="d-flex justify-content-between align-items-center mb-4">
                <h5 className="fw-bold mb-0">Recipients</h5>
                <div className="d-flex gap-2">
                  <label className="btn btn-secondary-custom mb-0 cursor-pointer">
                    <FileUp size={16} /> Upload CSV
                    <input type="file" accept=".csv" className="d-none" onChange={handleFileUpload} />
                  </label>
                  <button type="button" className="btn btn-secondary-custom" onClick={handleAddRecipient}>
                    <Plus size={16} /> Add Row
                  </button>
                </div>
              </div>
              
              <div className="table-container rounded" style={{ border: '1px solid var(--border)' }}>
                <table className="table-custom mb-0">
                  <thead>
                    <tr>
                      <th style={{ width: '40px' }}>#</th>
                      <th>Full Name</th>
                      <th>Email Address</th>
                      <th className="text-end">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recipients.map((r, i) => (
                      <tr key={i}>
                        <td className="fw-medium text-muted-custom">{i + 1}</td>
                        <td>
                          <input type="text" className="form-control-custom" placeholder="Jane Doe" required
                            style={{ padding: '6px 10px' }}
                            value={r.name} onChange={e => handleRecipientChange(i, 'name', e.target.value)} />
                        </td>
                        <td>
                          <input type="email" className="form-control-custom" placeholder="jane@example.com" required
                            style={{ padding: '6px 10px' }}
                            value={r.email} onChange={e => handleRecipientChange(i, 'email', e.target.value)} />
                        </td>
                        <td className="text-end">
                          <button type="button" className="btn btn-link text-danger p-1" onClick={() => handleRemoveRecipient(i)} disabled={recipients.length === 1}>
                            <Trash2 size={18} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          )}

          {step === 3 && (
            <motion.div key="step3" {...anim} transition={{ duration: 0.2 }}>
              <div className="text-center mb-5 mt-3">
                <div className="bg-primary bg-opacity-10 text-primary rounded-circle d-inline-flex align-items-center justify-content-center mb-4" style={{ width: 80, height: 80 }}>
                  <CheckCircle size={40} />
                </div>
                <h3 className="fw-bold">Ready to Generate?</h3>
                <p className="text-muted-custom mx-auto" style={{ maxWidth: 400 }}>
                  Please review the details below before starting the bulk generation process.
                </p>
              </div>

              <div className="row g-4 mb-4">
                <div className="col-md-6">
                  <div className="p-3 rounded" style={{ backgroundColor: 'var(--bg-app)', border: '1px solid var(--border)' }}>
                    <p className="small text-muted-custom mb-1 text-uppercase fw-bold">Job Details</p>
                    <p className="fw-medium mb-1">{formData.certificate_title}</p>
                    <p className="small mb-0">{formData.event_name} • {formData.organization_name}</p>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="p-3 rounded h-100" style={{ backgroundColor: 'var(--bg-app)', border: '1px solid var(--border)' }}>
                    <p className="small text-muted-custom mb-1 text-uppercase fw-bold">Recipients Summary</p>
                    <div className="d-flex justify-content-between align-items-center">
                      <span className="fw-medium">{validRecipients.length} Valid Recipients</span>
                      {invalidCount > 0 && (
                        <span className="badge-custom badge-warning">
                          <AlertTriangle size={12} /> {invalidCount} Invalid/Skipped
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="d-flex justify-content-between pt-5 mt-3 border-top" style={{ borderColor: 'var(--border)' }}>
          {step > 1 ? (
            <button type="button" className="btn btn-secondary-custom" onClick={() => setStep(step - 1)}>Back</button>
          ) : <div></div>}
          
          <button type="submit" className="btn btn-primary-custom" disabled={loading}>
            {loading ? <span className="spinner-border spinner-border-sm me-2" /> : null}
            {step === 3 ? 'Generate Certificates' : <span className="d-flex align-items-center">Continue <ChevronRight size={18} className="ms-1" /></span>}
          </button>
        </div>
      </form>
    </div>
  );
}
"""

job_details = """
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { jobsApi } from '../api/jobs';
import { FileText, CheckCircle2, XCircle, Clock, AlertTriangle, Download } from 'lucide-react';
import { motion } from 'framer-motion';

export default function JobDetails() {
  const { jobId } = useParams();
  const [job, setJob] = useState(null);
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);

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
        {/* Decorative background glow for active state */}
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
                  <tr key={c.certificate_id}>
                    <td className="font-monospace text-muted-custom small">{c.certificate_code}</td>
                    <td className="fw-medium">{c.recipient_name}</td>
                    <td>
                      {c.status === 'COMPLETED' ? <span className="badge-custom badge-success">Success</span> :
                       <span className="badge-custom badge-danger">Failed</span>}
                    </td>
                    <td className="text-danger small">{c.error_message || '-'}</td>
                    <td className="text-end">
                      {c.status === 'COMPLETED' && (
                        <a href={`${import.meta.env.VITE_API_BASE_URL}/api/v1/certificates/${c.certificate_id}/download`} 
                           target="_blank" rel="noreferrer"
                           className="btn btn-sm btn-secondary-custom">
                          <Download size={16} /> Download
                        </a>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </motion.div>
  );
}
"""

create_file("frontend/src/pages/CreateJob.jsx", create_job)
create_file("frontend/src/pages/JobDetails.jsx", job_details)
print("upgraded 3")
