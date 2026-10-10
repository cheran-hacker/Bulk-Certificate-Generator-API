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
import { Trash2, Plus, Upload, CheckCircle } from 'lucide-react';

export default function CreateJob() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    certificate_title: 'Certificate of Participation',
    event_name: '',
    organization_name: '',
    issue_date: new Date().toISOString().split('T')[0],
  });
  const [recipients, setRecipients] = useState([{ name: '', email: '' }]);

  const handleAddRecipient = () => {
    setRecipients([...recipients, { name: '', email: '' }]);
  };

  const handleRemoveRecipient = (index) => {
    const newRecipients = [...recipients];
    newRecipients.splice(index, 1);
    setRecipients(newRecipients);
  };

  const handleRecipientChange = (index, field, value) => {
    const newRecipients = [...recipients];
    newRecipients[index][field] = value;
    setRecipients(newRecipients);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Filter out empty rows
    const validRecipients = recipients.filter(r => r.name.trim() !== '' && r.email.trim() !== '');
    if (validRecipients.length === 0) {
      toast.error('Please add at least one valid recipient.');
      return;
    }

    const payload = {
      ...formData,
      recipients: validRecipients
    };

    try {
      setLoading(true);
      const res = await jobsApi.createJob(payload);
      toast.success('Job created successfully!');
      navigate(`/jobs/${res.data.job_id}`);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container-fluid py-4 max-w-4xl mx-auto">
      <div className="mb-4">
        <h2 className="fw-bold mb-1">Create Certificate Job</h2>
        <p className="text-muted mb-0">Generate certificates for multiple recipients using the predefined template.</p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="card-custom mb-4">
          <div className="p-4 border-bottom" style={{ borderColor: 'var(--border-color)' }}>
            <h5 className="fw-bold mb-0">Job Details</h5>
          </div>
          <div className="p-4 row g-3">
            <div className="col-md-6">
              <label className="form-label fw-medium">Certificate Title</label>
              <input type="text" className="form-control form-control-custom" required
                value={formData.certificate_title} onChange={e => setFormData({...formData, certificate_title: e.target.value})} />
            </div>
            <div className="col-md-6">
              <label className="form-label fw-medium">Event Name</label>
              <input type="text" className="form-control form-control-custom" required
                value={formData.event_name} onChange={e => setFormData({...formData, event_name: e.target.value})} />
            </div>
            <div className="col-md-6">
              <label className="form-label fw-medium">Organization Name</label>
              <input type="text" className="form-control form-control-custom" required
                value={formData.organization_name} onChange={e => setFormData({...formData, organization_name: e.target.value})} />
            </div>
            <div className="col-md-6">
              <label className="form-label fw-medium">Issue Date</label>
              <input type="date" className="form-control form-control-custom" required
                value={formData.issue_date} onChange={e => setFormData({...formData, issue_date: e.target.value})} />
            </div>
          </div>
        </div>

        <div className="card-custom mb-4">
          <div className="p-4 border-bottom d-flex justify-content-between align-items-center" style={{ borderColor: 'var(--border-color)' }}>
            <h5 className="fw-bold mb-0">Recipients</h5>
            <button type="button" className="btn btn-outline-primary btn-sm d-flex align-items-center" onClick={handleAddRecipient}>
              <Plus size={16} className="me-1" /> Add Row
            </button>
          </div>
          <div className="p-0 table-responsive">
            <table className="table table-custom mb-0">
              <thead className="bg-light">
                <tr>
                  <th className="px-4 py-3">#</th>
                  <th className="px-4 py-3">Full Name</th>
                  <th className="px-4 py-3">Email Address</th>
                  <th className="px-4 py-3 text-end">Action</th>
                </tr>
              </thead>
              <tbody>
                {recipients.map((recipient, index) => (
                  <tr key={index}>
                    <td className="px-4 py-3 align-middle">{index + 1}</td>
                    <td className="px-4 py-2">
                      <input type="text" className="form-control form-control-custom form-control-sm" placeholder="John Doe"
                        value={recipient.name} onChange={e => handleRecipientChange(index, 'name', e.target.value)} />
                    </td>
                    <td className="px-4 py-2">
                      <input type="email" className="form-control form-control-custom form-control-sm" placeholder="john@example.com"
                        value={recipient.email} onChange={e => handleRecipientChange(index, 'email', e.target.value)} />
                    </td>
                    <td className="px-4 py-3 text-end">
                      <button type="button" className="btn btn-link text-danger p-0" onClick={() => handleRemoveRecipient(index)} disabled={recipients.length === 1}>
                        <Trash2 size={18} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="d-flex justify-content-end gap-3">
          <button type="button" className="btn btn-light" onClick={() => navigate(-1)}>Cancel</button>
          <button type="submit" className="btn btn-primary-custom d-flex align-items-center" disabled={loading}>
            {loading ? <span className="spinner-border spinner-border-sm me-2" /> : <CheckCircle size={18} className="me-2" />}
            Generate Certificates
          </button>
        </div>
      </form>
    </div>
  );
}
"""

job_details = """
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { jobsApi } from '../api/jobs';
import { FileText, CheckCircle, XCircle, Clock, AlertTriangle } from 'lucide-react';

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
          // Fetch certificates once done
          const certRes = await jobsApi.getJobCertificates(jobId);
          setCertificates(certRes.data);
        }
      } catch (err) {
        clearInterval(interval);
      } finally {
        setLoading(false);
      }
    };

    fetchJob();
    interval = setInterval(fetchJob, 2000);

    return () => clearInterval(interval);
  }, [jobId]);

  if (loading) return <div className="p-5 text-center"><span className="spinner-border text-primary" /></div>;
  if (!job) return <div className="p-5 text-center">Job not found.</div>;

  const getStatusBadge = (status) => {
    switch(status) {
      case 'COMPLETED': return <span className="badge badge-status badge-success">Completed</span>;
      case 'COMPLETED_WITH_ERRORS': return <span className="badge badge-status badge-warning">Completed with Errors</span>;
      case 'FAILED': return <span className="badge badge-status badge-danger">Failed</span>;
      case 'PROCESSING': return <span className="badge badge-status badge-info">Processing</span>;
      default: return <span className="badge badge-status bg-secondary">Pending</span>;
    }
  };

  return (
    <div className="container-fluid py-4">
      <div className="mb-4 d-flex justify-content-between align-items-center">
        <div>
          <h2 className="fw-bold mb-1">Job Details</h2>
          <p className="text-muted mb-0">ID: {job.job_id}</p>
        </div>
        <div>{getStatusBadge(job.status)}</div>
      </div>

      <div className="row g-4 mb-4">
        <div className="col-12">
          <div className="card-custom p-4">
            <h5 className="fw-bold mb-3">Generation Progress</h5>
            <div className="d-flex justify-content-between mb-1">
              <span className="fw-medium">{job.progress_percentage}%</span>
              <span className="text-muted small">{job.success_count + job.failed_count} / {job.total_recipients} processed</span>
            </div>
            <div className="progress" style={{ height: '10px' }}>
              <div className="progress-bar bg-primary" role="progressbar" style={{ width: `${job.progress_percentage}%` }}></div>
            </div>
            
            <div className="d-flex gap-4 mt-4">
              <div className="d-flex align-items-center gap-2">
                <CheckCircle size={20} className="text-success" />
                <span className="fw-medium">{job.success_count} Successful</span>
              </div>
              <div className="d-flex align-items-center gap-2">
                <XCircle size={20} className="text-danger" />
                <span className="fw-medium">{job.failed_count} Failed</span>
              </div>
              <div className="d-flex align-items-center gap-2">
                <Clock size={20} className="text-muted" />
                <span className="fw-medium">{job.pending_count} Pending</span>
              </div>
            </div>
            
            {job.status === 'COMPLETED_WITH_ERRORS' && (
              <div className="alert alert-warning mt-4 mb-0 d-flex align-items-center">
                <AlertTriangle size={20} className="me-2" />
                Some certificates failed to generate. Check the records below for details.
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="card-custom">
        <div className="p-4 border-bottom" style={{ borderColor: 'var(--border-color)' }}>
          <h5 className="fw-bold mb-0">Certificates</h5>
        </div>
        {certificates.length === 0 ? (
          <div className="p-5 text-center text-muted">
            <p>Certificates will appear here once processing completes.</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="table table-custom mb-0">
              <thead className="bg-light">
                <tr>
                  <th className="px-4 py-3">Code</th>
                  <th className="px-4 py-3">Recipient Name</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Error</th>
                  <th className="px-4 py-3 text-end">Action</th>
                </tr>
              </thead>
              <tbody>
                {certificates.map(c => (
                  <tr key={c.certificate_id}>
                    <td className="px-4 py-3"><small className="text-muted">{c.certificate_code}</small></td>
                    <td className="px-4 py-3 fw-medium">{c.recipient_name}</td>
                    <td className="px-4 py-3">
                      {c.status === 'COMPLETED' ? (
                         <span className="badge badge-status badge-success">Success</span>
                      ) : (
                         <span className="badge badge-status badge-danger">Failed</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-danger small">{c.error_message || '-'}</td>
                    <td className="px-4 py-3 text-end">
                      {c.status === 'COMPLETED' && (
                        <a href={`${import.meta.env.VITE_API_BASE_URL}/api/v1/certificates/${c.certificate_id}/download`} 
                           target="_blank" rel="noreferrer"
                           className="btn btn-sm btn-outline-primary d-inline-flex align-items-center">
                          <FileText size={16} className="me-1" /> PDF
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
    </div>
  );
}
"""

certificates_list = """
import { useState } from 'react';
import { Search } from 'lucide-react';

export default function Certificates() {
  // Mocking the page layout since we don't have a global search API endpoint 
  // without a job_id in the current backend spec.
  // The backend has /api/v1/jobs/{job_id}/certificates, but not a global /api/v1/certificates listing.
  // We will display an empty state for this page or instruct the user to view jobs.
  
  return (
    <div className="container-fluid py-4">
      <div className="mb-4">
        <h2 className="fw-bold mb-1">Certificates</h2>
        <p className="text-muted mb-0">Search and manage all generated certificates across jobs.</p>
      </div>

      <div className="card-custom text-center p-5">
        <div className="mb-3 text-muted">
          <Search size={48} />
        </div>
        <h4 className="fw-bold">Global Certificate Search</h4>
        <p className="text-muted max-w-md mx-auto">
          To view generated certificates, please navigate to the specific Job from the Dashboard.
        </p>
      </div>
    </div>
  );
}
"""

create_file("frontend/src/pages/CreateJob.jsx", create_job)
create_file("frontend/src/pages/JobDetails.jsx", job_details)
create_file("frontend/src/pages/Certificates.jsx", certificates_list)
print("Generated job pages")
