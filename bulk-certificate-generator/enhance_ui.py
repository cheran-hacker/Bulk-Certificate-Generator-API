import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())

dashboard = """
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
"""

settings = """
import { motion } from 'framer-motion';
import { useTheme } from '../hooks/useTheme';
import { User, Shield, Bell, Palette, Database } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Settings() {
  const { theme, toggleTheme } = useTheme();

  const handleSave = () => {
    toast.success('Preferences saved successfully.');
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="container-fluid py-2 max-w-4xl mx-auto" style={{ maxWidth: 900 }}>
      <div className="mb-5">
        <h2 className="fw-bold mb-1">Settings</h2>
        <p className="text-muted-custom mb-0">Manage your application preferences and configurations.</p>
      </div>

      <div className="row g-4">
        <div className="col-md-4">
          <ul className="nav flex-column gap-2 sticky-top" style={{ top: 100 }}>
            <li className="nav-item">
              <a className="nav-link active d-flex align-items-center fw-medium bg-primary text-white rounded" href="#appearance">
                <Palette size={18} className="me-3" /> Appearance
              </a>
            </li>
            <li className="nav-item">
              <a className="nav-link d-flex align-items-center fw-medium text-muted-custom hover-bg-surface rounded" href="#notifications">
                <Bell size={18} className="me-3" /> Notifications
              </a>
            </li>
            <li className="nav-item">
              <a className="nav-link d-flex align-items-center fw-medium text-muted-custom hover-bg-surface rounded" href="#api">
                <Database size={18} className="me-3" /> API Configuration
              </a>
            </li>
          </ul>
        </div>
        
        <div className="col-md-8">
          
          <div id="appearance" className="surface p-4 p-md-5 mb-4">
            <h5 className="fw-bold mb-4 pb-3 border-bottom" style={{ borderColor: 'var(--border)' }}>Appearance</h5>
            
            <div className="mb-4">
              <label className="fw-semibold d-block mb-3">Theme Preference</label>
              <div className="d-flex gap-3">
                <button 
                  onClick={() => theme === 'dark' && toggleTheme()}
                  className={`btn d-flex flex-column align-items-center justify-content-center p-3 rounded-3 border ${theme === 'light' ? 'border-primary bg-primary bg-opacity-10' : 'border-secondary'}`}
                  style={{ width: 120, height: 100 }}>
                  <div className="rounded-circle bg-light border mb-2 shadow-sm" style={{ width: 30, height: 30 }}></div>
                  <span className={`small fw-medium ${theme === 'light' ? 'text-primary' : 'text-muted-custom'}`}>Light</span>
                </button>
                <button 
                  onClick={() => theme === 'light' && toggleTheme()}
                  className={`btn d-flex flex-column align-items-center justify-content-center p-3 rounded-3 border ${theme === 'dark' ? 'border-primary bg-primary bg-opacity-10' : 'border-secondary'}`}
                  style={{ width: 120, height: 100, backgroundColor: 'var(--bg-app)' }}>
                  <div className="rounded-circle bg-dark border border-secondary mb-2 shadow-sm" style={{ width: 30, height: 30 }}></div>
                  <span className={`small fw-medium ${theme === 'dark' ? 'text-primary' : 'text-muted-custom'}`}>Dark</span>
                </button>
              </div>
            </div>
          </div>

          <div id="notifications" className="surface p-4 p-md-5 mb-4 opacity-75">
            <h5 className="fw-bold mb-4 pb-3 border-bottom" style={{ borderColor: 'var(--border)' }}>Notifications <span className="badge bg-secondary ms-2 fw-normal" style={{ fontSize: 10 }}>Coming Soon</span></h5>
            
            <div className="form-check form-switch mb-3">
              <input className="form-check-input" type="checkbox" id="emailNotif" disabled />
              <label className="form-check-label fw-medium" htmlFor="emailNotif">Email on Job Completion</label>
            </div>
            <div className="form-check form-switch">
              <input className="form-check-input" type="checkbox" id="failNotif" disabled checked />
              <label className="form-check-label fw-medium" htmlFor="failNotif">Alert on Certificate Failures</label>
            </div>
          </div>

          <div className="d-flex justify-content-end mb-5">
            <button className="btn btn-primary-custom" onClick={handleSave}>Save Preferences</button>
          </div>

        </div>
      </div>
    </motion.div>
  );
}
"""

sidebar = """
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, FilePlus2, Layers, BookOpen, Settings, PanelLeftClose, PanelLeftOpen } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Sidebar({ isOpen, toggle }) {
  const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/jobs', icon: Layers, label: 'Jobs' },
    { to: '/jobs/create', icon: FilePlus2, label: 'Create Job' }
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
          <Route path="settings" element={<Settings />} />
          <Route path="docs" element={<Navigate to={() => { window.open(import.meta.env.VITE_API_BASE_URL + '/docs', '_blank'); return null; }} />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </>
  );
}
"""

create_file("frontend/src/pages/Dashboard.jsx", dashboard)
create_file("frontend/src/pages/Settings.jsx", settings)
create_file("frontend/src/components/Sidebar.jsx", sidebar)
create_file("frontend/src/App.jsx", app_jsx)
print("Enhancements applied successfully")
