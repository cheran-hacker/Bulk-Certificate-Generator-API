import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())

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
            <div className="bg-primary text-white rounded p-1 d-flex align-items-center justify-content-center" style={{ width: 32, height: 32 }}>
               <span className="fw-bold fs-5" style={{ lineHeight: 1 }}>C</span>
            </div>
            <span className="fs-5 fw-bold" style={{ color: 'var(--text-main)', letterSpacing: '-0.5px' }}>CertiFlow</span>
          </motion.div>
        ) : (
          <div className="w-100 d-flex justify-content-center">
            <div className="bg-primary text-white rounded p-1 d-flex align-items-center justify-content-center" style={{ width: 32, height: 32 }}>
               <span className="fw-bold fs-5" style={{ lineHeight: 1 }}>C</span>
            </div>
          </div>
        )}
      </div>
      
      <div className="px-3 mb-2">
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

navbar = """
import { Sun, Moon, Bell, Search } from 'lucide-react';
import { useEffect, useState } from 'react';
import { healthApi } from '../api/health';
import { useLocation } from 'react-router-dom';

export default function Navbar({ theme, toggleTheme }) {
  const [apiStatus, setApiStatus] = useState('Checking...');
  const [isUp, setIsUp] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const check = async () => {
      try {
        const res = await healthApi.checkHealth();
        setApiStatus('Connected');
        setIsUp(true);
      } catch (e) {
        setApiStatus('Disconnected');
        setIsUp(false);
      }
    };
    check();
    const int = setInterval(check, 30000);
    return () => clearInterval(int);
  }, []);

  const getPageTitle = () => {
    if (location.pathname === '/') return 'Dashboard';
    if (location.pathname === '/jobs') return 'Jobs Overview';
    if (location.pathname === '/jobs/create') return 'Create Certificate Job';
    if (location.pathname.startsWith('/jobs/')) return 'Job Details';
    return 'Dashboard';
  };

  return (
    <header className="d-flex align-items-center justify-content-between px-4" 
            style={{ 
              height: 'var(--navbar-h)', 
              backgroundColor: 'var(--bg-app)',
              position: 'sticky',
              top: 0,
              zIndex: 10
            }}>
      
      <div className="d-flex align-items-center">
        <div>
          <h4 className="mb-0 fw-bold" style={{ color: 'var(--text-main)', letterSpacing: '-0.5px' }}>{getPageTitle()}</h4>
        </div>
      </div>
      
      <div className="d-flex align-items-center gap-4">
        
        <div className="d-flex align-items-center gap-2 bg-surface px-3 py-1 rounded-pill" style={{ border: '1px solid var(--border)' }}>
          <div className={isUp ? 'animate-pulse-subtle' : ''} style={{ 
            width: 8, height: 8, borderRadius: '50%', 
            backgroundColor: isUp ? 'var(--success)' : 'var(--danger)' 
          }}></div>
          <span className="small fw-medium" style={{ color: 'var(--text-muted)' }}>API {apiStatus}</span>
        </div>
        
        <div className="d-flex align-items-center gap-1">
          <button className="btn btn-link p-2 rounded-circle" onClick={toggleTheme} style={{ color: 'var(--text-muted)' }}>
            {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
          </button>
          
          <button className="btn btn-link p-2 rounded-circle" style={{ color: 'var(--text-muted)' }}>
            <Bell size={20} />
          </button>
          
          <div className="ms-3" style={{ width: 36, height: 36, borderRadius: '50%', backgroundColor: 'var(--primary)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600 }}>
            US
          </div>
        </div>
      </div>
    </header>
  );
}
"""

dashboard = """
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Plus, CheckCircle2, XCircle, Layers, Activity } from 'lucide-react';
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
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const res = await jobsApi.getJobs(0, 100); // Fetch recent 100 to aggregate
        const jobs = res.items || [];
        
        let totalCerts = 0;
        let successful = 0;
        let failed = 0;
        
        jobs.forEach(j => {
          totalCerts += j.total_recipients;
          successful += j.success_count;
          failed += j.failed_count;
        });
        
        setStats({
          totalJobs: res.total || jobs.length,
          totalCerts,
          successful,
          failed,
          rate: totalCerts > 0 ? ((successful / totalCerts) * 100).toFixed(1) : 0
        });
        
        setRecentJobs(jobs.slice(0, 5)); // Show top 5
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
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="container-fluid py-2">
      <motion.div variants={item} className="d-flex justify-content-between align-items-end mb-5">
        <div>
          <h5 className="fw-semibold text-muted-custom mb-1">Good to see you</h5>
          <h2 className="fw-bold mb-0">Your certificate operations, all in one place.</h2>
        </div>
        <div className="d-flex gap-3">
          <Link to="/jobs" className="btn btn-secondary-custom">View All Jobs</Link>
          <Link to="/jobs/create" className="btn btn-primary-custom">
            <Plus size={20} /> Create Job
          </Link>
        </div>
      </motion.div>
      
      {loading ? (
        <div className="row g-4 mb-5">
          {[1,2,3,4].map(i => (
            <div key={i} className="col-md-3">
              <div className="surface p-4 animate-pulse-subtle" style={{ height: 120 }}></div>
            </div>
          ))}
        </div>
      ) : (
        <motion.div variants={item} className="row g-4 mb-5">
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

      <motion.div variants={item} className="surface overflow-hidden">
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
                       <div className="progress flex-grow-1" style={{ height: 6, backgroundColor: 'var(--border)' }}>
                         <div className="progress-bar bg-primary" style={{ width: `${job.progress_percentage}%` }}></div>
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
      </motion.div>
    </motion.div>
  );
}
"""

create_file("frontend/src/components/Sidebar.jsx", sidebar)
create_file("frontend/src/components/Navbar.jsx", navbar)
create_file("frontend/src/pages/Dashboard.jsx", dashboard)
print("upgraded 2")
