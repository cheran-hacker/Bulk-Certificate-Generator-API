import { NavLink } from 'react-router-dom';
import { LayoutDashboard, FilePlus2, Layers, BookOpen, Settings, PanelLeftClose, PanelLeftOpen, FileText } from 'lucide-react';
import { motion } from 'framer-motion';

export default function Sidebar({ isOpen, toggle }) {
  const navItems = [
    { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/jobs', icon: Layers, label: 'Jobs' },
    { to: '/jobs/create', icon: FilePlus2, label: 'Create Job' },
    { to: '/certificates', icon: FileText, label: 'Certificates' }
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