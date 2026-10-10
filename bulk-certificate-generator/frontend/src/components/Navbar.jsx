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