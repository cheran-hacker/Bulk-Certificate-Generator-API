import os

def create_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content.strip())

layout = """
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Navbar from './Navbar';
import { useTheme } from '../hooks/useTheme';
import { useState } from 'react';

export default function Layout() {
  const { theme, toggleTheme } = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="d-flex" style={{ minHeight: '100vh', backgroundColor: 'var(--bg-color)' }}>
      <Sidebar isOpen={sidebarOpen} toggle={() => setSidebarOpen(!sidebarOpen)} />
      <div className="flex-grow-1 d-flex flex-column" style={{ transition: 'margin-left 0.3s' }}>
        <Navbar theme={theme} toggleTheme={toggleTheme} toggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
        <main className="p-4" style={{ flexGrow: 1, overflowY: 'auto' }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
"""

sidebar = """
import { NavLink } from 'react-router-dom';
import { Home, PlusSquare, FileText, List, BarChart2, Settings, BookOpen, ChevronLeft, ChevronRight } from 'lucide-react';

export default function Sidebar({ isOpen, toggle }) {
  const navItems = [
    { to: '/', icon: Home, label: 'Dashboard' },
    { to: '/jobs/create', icon: PlusSquare, label: 'Create Job' },
    { to: '/certificates', icon: FileText, label: 'Certificates' },
    { to: '/jobs', icon: List, label: 'Jobs' },
    { to: '/docs', icon: BookOpen, label: 'API Documentation' },
  ];

  return (
    <div className="d-flex flex-column flex-shrink-0 p-3" 
         style={{ 
           width: isOpen ? '250px' : '80px', 
           backgroundColor: 'var(--surface-color)', 
           borderRight: '1px solid var(--border-color)',
           transition: 'width 0.3s',
           height: '100vh',
           position: 'sticky',
           top: 0
         }}>
      <div className="d-flex align-items-center justify-content-between mb-3 mb-md-0 me-md-auto text-decoration-none">
        <span className="fs-4 fw-bold" style={{ color: 'var(--primary-color)', display: isOpen ? 'block' : 'none' }}>CertiFlow</span>
        {isOpen ? null : <span className="fs-4 fw-bold text-center w-100" style={{ color: 'var(--primary-color)' }}>CF</span>}
      </div>
      <hr style={{ borderColor: 'var(--border-color)' }} />
      <ul className="nav nav-pills flex-column mb-auto">
        {navItems.map((item) => (
          <li className="nav-item mb-2" key={item.to}>
            <NavLink 
              to={item.to} 
              className={({ isActive }) => `nav-link d-flex align-items-center ${isActive ? 'active' : ''}`}
              style={({ isActive }) => ({
                backgroundColor: isActive ? 'var(--primary-color)' : 'transparent',
                color: isActive ? 'white' : 'var(--text-primary)',
                justifyContent: isOpen ? 'flex-start' : 'center',
                padding: '10px 15px',
                borderRadius: '8px'
              })}
            >
              <item.icon size={20} className={isOpen ? "me-3" : ""} />
              {isOpen && <span>{item.label}</span>}
            </NavLink>
          </li>
        ))}
      </ul>
      <hr style={{ borderColor: 'var(--border-color)' }} />
      <button className="btn btn-link text-decoration-none d-flex align-items-center" 
              onClick={toggle}
              style={{ color: 'var(--text-secondary)', justifyContent: isOpen ? 'flex-start' : 'center' }}>
        {isOpen ? <ChevronLeft size={20} className="me-2" /> : <ChevronRight size={20} />}
        {isOpen && <span>Collapse Sidebar</span>}
      </button>
    </div>
  );
}
"""

navbar = """
import { Sun, Moon, Bell, Menu } from 'lucide-react';
import { useEffect, useState } from 'react';
import { healthApi } from '../api/health';

export default function Navbar({ theme, toggleTheme, toggleSidebar }) {
  const [apiStatus, setApiStatus] = useState('Checking...');
  const [isUp, setIsUp] = useState(false);

  useEffect(() => {
    const check = async () => {
      try {
        const res = await healthApi.checkHealth();
        setApiStatus(res.status === 'ok' ? 'Connected' : 'Degraded');
        setIsUp(res.status === 'ok');
      } catch (e) {
        setApiStatus('Disconnected');
        setIsUp(false);
      }
    };
    check();
    const int = setInterval(check, 30000);
    return () => clearInterval(int);
  }, []);

  return (
    <header className="d-flex align-items-center justify-content-between px-4" 
            style={{ 
              height: 'var(--navbar-height)', 
              backgroundColor: 'var(--surface-color)',
              borderBottom: '1px solid var(--border-color)',
              position: 'sticky',
              top: 0,
              zIndex: 10
            }}>
      <div className="d-flex align-items-center">
        <button className="btn btn-link d-md-none me-2" onClick={toggleSidebar} style={{ color: 'var(--text-primary)' }}>
          <Menu size={24} />
        </button>
        <h5 className="mb-0 fw-semibold" style={{ color: 'var(--text-primary)' }}>Dashboard</h5>
      </div>
      
      <div className="d-flex align-items-center gap-4">
        <div className="d-flex align-items-center gap-2">
          <span style={{ 
            width: 10, height: 10, borderRadius: '50%', 
            backgroundColor: isUp ? 'var(--success)' : 'var(--danger)' 
          }}></span>
          <span className="small text-muted fw-medium">API: {apiStatus}</span>
        </div>
        
        <button className="btn btn-link p-0" onClick={toggleTheme} style={{ color: 'var(--text-secondary)' }}>
          {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
        </button>
        
        <button className="btn btn-link p-0" style={{ color: 'var(--text-secondary)' }}>
          <Bell size={20} />
        </button>
      </div>
    </header>
  );
}
"""

create_file("frontend/src/components/Layout.jsx", layout)
create_file("frontend/src/components/Sidebar.jsx", sidebar)
create_file("frontend/src/components/Navbar.jsx", navbar)
print("Generated layout components")
