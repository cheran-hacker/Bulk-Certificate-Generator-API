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
    event_name: 'Annual Tech Summit',
    organization_name: 'Tech Innovators Inc.',
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
    
    if (step === 1) {
      if (!formData.certificate_title.trim() || !formData.event_name.trim() || !formData.organization_name.trim()) {
        toast.error("Please fill in all required job details.");
        return;
      }
      return setStep(2);
    }
    
    if (step === 2) {
      if (validRecipients.length === 0) {
        toast.error('Please add at least one valid recipient with a correct email.');
        return;
      }
      return setStep(3);
    }
    
    try {
      setLoading(true);
      const res = await jobsApi.createJob({ ...formData, recipients: validRecipients });
      toast.success('Generation job queued successfully!');
      navigate(`/jobs/${res.data.job_id}`);
    } catch (err) {
      console.error(err);
      if (err.response && err.response.status === 422) {
        const detail = err.response.data.detail;
        if (Array.isArray(detail) && detail.length > 0) {
          toast.error(`Validation Error: ${detail[0].loc.join('.')} - ${detail[0].msg}`);
        } else {
          toast.error('Invalid data submitted. Please check your inputs.');
        }
      } else {
        toast.error('An unexpected error occurred.');
      }
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
                          <input type="text" className="form-control-custom" placeholder="Jane Doe" required={i===0}
                            style={{ padding: '6px 10px' }}
                            value={r.name} onChange={e => handleRecipientChange(i, 'name', e.target.value)} />
                        </td>
                        <td>
                          <input type="email" className="form-control-custom" placeholder="jane@example.com" required={i===0}
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

create_file("frontend/src/pages/CreateJob.jsx", create_job)
print("Validation fixed")
