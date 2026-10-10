import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { jobsApi } from '../api/jobs';
import { motion } from 'framer-motion';
import { Plus, Search, Layers, RefreshCw } from 'lucide-react';

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const res = await jobsApi.getJobs(0, 100);
      setJobs(res.items || []);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const filteredJobs = jobs.filter(j => j.id.toLowerCase().includes(search.toLowerCase()) || j.status.toLowerCase().includes(search.toLowerCase()));

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="container-fluid py-2">
      <div className="mb-4 d-flex justify-content-between align-items-end">
        <div>
          <h2 className="fw-bold mb-1">Jobs Overview</h2>
          <p className="text-muted-custom mb-0">Manage all bulk certificate generation jobs.</p>
        </div>
        <Link to="/jobs/create" className="btn btn-primary-custom">
          <Plus size={20} /> Create Job
        </Link>
      </div>

      <div className="surface overflow-hidden">
        <div className="p-4 border-bottom d-flex justify-content-between align-items-center" style={{ borderColor: 'var(--border)' }}>
          <div className="position-relative" style={{ width: 300 }}>
            <Search size={18} className="position-absolute text-muted-custom" style={{ top: 11, left: 12 }} />
            <input type="text" className="form-control-custom ps-5" placeholder="Search by Job ID or Status..."
                   value={search} onChange={e => setSearch(e.target.value)} />
          </div>
          <button className="btn btn-secondary-custom" onClick={fetchJobs} disabled={loading}>
            <RefreshCw size={18} className={loading ? 'animate-pulse-subtle' : ''} /> Refresh
          </button>
        </div>

        <div className="table-container">
          <table className="table-custom">
            <thead>
              <tr>
                <th>Job ID</th>
                <th>Status</th>
                <th>Progress</th>
                <th>Total</th>
                <th>Date</th>
                <th className="text-end">Action</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="6" className="text-center py-5">
                    <span className="spinner-border text-primary opacity-50" />
                  </td>
                </tr>
              ) : filteredJobs.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center py-5 text-muted-custom">
                     <Layers size={48} className="mb-3 opacity-50 mx-auto" />
                     <p className="mb-0">No jobs found matching your criteria.</p>
                  </td>
                </tr>
              ) : (
                filteredJobs.map(job => (
                  <tr key={job.id}>
                    <td className="fw-medium font-monospace small">{job.id}</td>
                    <td>
                      {job.status === 'COMPLETED' ? <span className="badge-custom badge-success">Completed</span> :
                       job.status === 'COMPLETED_WITH_ERRORS' ? <span className="badge-custom badge-warning">Partial Errors</span> :
                       job.status === 'FAILED' ? <span className="badge-custom badge-danger">Failed</span> :
                       <span className="badge-custom badge-info">Processing</span>}
                    </td>
                    <td>
                       <div className="d-flex align-items-center gap-2">
                         <div className="progress flex-grow-1" style={{ height: 6, backgroundColor: 'var(--border)' }}>
                           <div className="progress-bar bg-primary" style={{ width: `${job.progress_percentage}%` }}></div>
                         </div>
                         <span className="small text-muted-custom fw-medium" style={{ width: 40 }}>{Math.round(job.progress_percentage)}%</span>
                       </div>
                    </td>
                    <td className="text-muted-custom">{job.total_recipients}</td>
                    <td className="text-muted-custom small">{new Date(job.created_at).toLocaleString()}</td>
                    <td className="text-end">
                      <Link to={`/jobs/${job.id}`} className="btn btn-sm btn-secondary-custom">View Details</Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
}