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