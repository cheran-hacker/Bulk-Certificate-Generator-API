import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Plus, CheckCircle2, XCircle, Layers, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { jobsApi } from '../api/jobs';

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalJobs: 0,
    totalCerts: 0,
    successful: 0,
    failed: 0,
    rate: 0
  });
  const [recentJobs, setRecentJobs] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const res = await jobsApi.getJobs(0, 100); 
        const jobs = res.items || [];
        
        let totalCerts = 0;
        let successful = 0;
        let failed = 0;
        
        const cData = [];

        jobs.forEach((j, i) => {
          totalCerts += j.total_recipients;
          successful += j.success_count;
          failed += j.failed_count;
          
          if (i < 7) { // Last 7 jobs for the chart
             cData.unshift({
               name: `Job ${j.id.split('-')[0]}`,
               Successful: j.success_count,
               Failed: j.failed_count
             });
          }
        });
        
        setStats({
          totalJobs: res.total || jobs.length,
          totalCerts,
          successful,
          failed,
          rate: totalCerts > 0 ? ((successful / totalCerts) * 100).toFixed(1) : 0
        });
        
        setChartData(cData);
        setRecentJobs(jobs.slice(0, 5));
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);

  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.1 } }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="container-fluid py-2">
      <motion.div variants={item} className="d-flex justify-content-between align-items-end mb-4">
        <div>
          <h5 className="fw-semibold text-muted-custom mb-1">Good to see you</h5>
          <h2 className="fw-bold mb-0">Your certificate operations, all in one place.</h2>
        </div>
        <div className="d-flex gap-3">
          <Link to="/jobs" className="btn btn-secondary-custom">View All Jobs</Link>
          <Link to="/jobs/create" className="btn btn-primary-custom shadow-sm">
            <Plus size={20} /> Create Job
          </Link>
        </div>
      </motion.div>
      
      {loading ? (
        <div className="row g-4 mb-4">
          {[1,2,3,4].map(i => (
            <div key={i} className="col-md-3">
              <div className="surface p-4 animate-pulse-subtle" style={{ height: 120 }}></div>
            </div>
          ))}
        </div>
      ) : (
        <motion.div variants={item} className="row g-4 mb-4">
          <div className="col-md-3">
            <div className="surface p-4 h-100 surface-hover">
              <div className="d-flex align-items-center mb-3">
                <Layers size={20} className="me-2 text-primary" />
                <h6 className="mb-0 text-muted-custom fw-semibold">Total Jobs</h6>
              </div>
              <h2 className="fw-bold mb-0">{stats.totalJobs}</h2>
            </div>
          </div>
          <div className="col-md-3">
            <div className="surface p-4 h-100 surface-hover">
              <div className="d-flex align-items-center mb-3">
                <Activity size={20} className="me-2 text-info" />
                <h6 className="mb-0 text-muted-custom fw-semibold">Generated</h6>
              </div>
              <h2 className="fw-bold mb-0">{stats.successful}</h2>
            </div>
          </div>
          <div className="col-md-3">
            <div className="surface p-4 h-100 surface-hover">
              <div className="d-flex align-items-center mb-3">
                <CheckCircle2 size={20} className="me-2 text-success" />
                <h6 className="mb-0 text-muted-custom fw-semibold">Success Rate</h6>
              </div>
              <h2 className="fw-bold mb-0">{stats.rate}%</h2>
            </div>
          </div>
          <div className="col-md-3">
            <div className="surface p-4 h-100 surface-hover">
              <div className="d-flex align-items-center mb-3">
                <XCircle size={20} className="me-2 text-danger" />
                <h6 className="mb-0 text-muted-custom fw-semibold">Failed Certs</h6>
              </div>
              <h2 className="fw-bold mb-0">{stats.failed}</h2>
            </div>
          </div>
        </motion.div>
      )}

      <div className="row g-4">
        <motion.div variants={item} className="col-xl-8">
          <div className="surface overflow-hidden h-100">
            <div className="px-4 py-4 border-bottom d-flex justify-content-between align-items-center" style={{ borderColor: 'var(--border)' }}>
              <h5 className="fw-bold mb-0">Recent Activity</h5>
              <Link to="/jobs" className="text-decoration-none fw-medium text-primary">View all →</Link>
            </div>
            
            <div className="table-container">
              <table className="table-custom">
                <thead>
                  <tr>
                    <th>Job ID</th>
                    <th>Status</th>
                    <th>Progress</th>
                    <th>Date</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {recentJobs.length === 0 && !loading && (
                    <tr>
                      <td colSpan="5" className="text-center py-5 text-muted-custom">
                         <Layers size={48} className="mb-3 opacity-50 mx-auto" />
                         <p className="mb-0">No jobs found. Create your first bulk job.</p>
                      </td>
                    </tr>
                  )}
                  {recentJobs.map(job => (
                    <tr key={job.id}>
                      <td className="fw-medium font-monospace small">{job.id.split('-')[0]}...</td>
                      <td>
                        {job.status === 'COMPLETED' ? <span className="badge-custom badge-success">Completed</span> :
                         job.status === 'COMPLETED_WITH_ERRORS' ? <span className="badge-custom badge-warning">Partial Errors</span> :
                         job.status === 'FAILED' ? <span className="badge-custom badge-danger">Failed</span> :
                         <span className="badge-custom badge-info">Processing</span>}
                      </td>
                      <td>
                         <div className="d-flex align-items-center gap-2">
                           <div className="progress flex-grow-1 bg-light rounded-pill" style={{ height: 6, backgroundColor: 'var(--border)' }}>
                             <div className="progress-bar bg-primary rounded-pill" style={{ width: `${job.progress_percentage}%` }}></div>
                           </div>
                           <span className="small text-muted-custom fw-medium" style={{ width: 40 }}>{Math.round(job.progress_percentage)}%</span>
                         </div>
                      </td>
                      <td className="text-muted-custom small">{new Date(job.created_at).toLocaleDateString()}</td>
                      <td>
                        <Link to={`/jobs/${job.id}`} className="btn btn-sm btn-link text-decoration-none fw-medium p-0">Details</Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>

        <motion.div variants={item} className="col-xl-4">
           <div className="surface p-4 h-100 d-flex flex-column">
              <h5 className="fw-bold mb-4">Generation Volume</h5>
              {chartData.length > 0 ? (
                <div className="flex-grow-1" style={{ minHeight: 250 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                      <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: 'var(--text-muted)', fontSize: 12}} />
                      <YAxis axisLine={false} tickLine={false} tick={{fill: 'var(--text-muted)', fontSize: 12}} />
                      <Tooltip 
                        contentStyle={{ backgroundColor: 'var(--bg-surface)', borderColor: 'var(--border)', borderRadius: 8, color: 'var(--text-main)' }}
                        itemStyle={{ fontWeight: 600 }}
                      />
                      <Legend iconType="circle" wrapperStyle={{ fontSize: 12, paddingTop: 10 }} />
                      <Bar dataKey="Successful" fill="var(--success)" radius={[4, 4, 0, 0]} maxBarSize={40} />
                      <Bar dataKey="Failed" fill="var(--danger)" radius={[4, 4, 0, 0]} maxBarSize={40} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="flex-grow-1 d-flex align-items-center justify-content-center text-muted-custom">
                  <p>Not enough data to display charts.</p>
                </div>
              )}
           </div>
        </motion.div>
      </div>
    </motion.div>
  );
}