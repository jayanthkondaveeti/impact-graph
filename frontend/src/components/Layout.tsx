import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Settings as SettingsIcon, LogOut, ShieldAlert } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/login');
  };

  const menuItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={20} /> },
    { name: 'Settings', path: '/settings', icon: <SettingsIcon size={20} /> },
  ];

  return (
    <div style={styles.appContainer}>
      {/* Sidebar Navigation */}
      <aside style={styles.sidebar}>
        <div style={styles.logoArea}>
          <div style={styles.logoIcon}>
            <ShieldAlert size={20} color="white" />
          </div>
          <span style={styles.logoText}>ImpactGraph</span>
        </div>
        
        <nav style={styles.navLinks}>
          {menuItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link 
                key={item.name} 
                to={item.path} 
                style={{
                  ...styles.navItem,
                  ...(isActive ? styles.navItemActive : {})
                }}
              >
                {item.icon}
                <span>{item.name}</span>
              </Link>
            );
          })}
        </nav>
        
        <div style={styles.sidebarFooter}>
          <button onClick={handleLogout} style={styles.logoutBtn}>
            <LogOut size={20} />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content Pane */}
      <div style={styles.mainPane}>
        <header style={styles.header}>
          <h2>
            {location.pathname === '/' ? 'Operational Workspace' : 
             location.pathname === '/settings' ? 'Connector Configuration' : 'Workspace'}
          </h2>
          <div style={styles.userBadge}>
            <div style={styles.avatar}>A</div>
            <span>Admin</span>
          </div>
        </header>
        <main style={styles.contentArea}>
          {children}
        </main>
      </div>
    </div>
  );
};

// Inline CSS Styles for local self-containment
const styles: Record<string, React.CSSProperties> = {
  appContainer: {
    display: 'flex',
    height: '100vh',
    width: '100vw',
    backgroundColor: '#0a0e1a',
    fontFamily: "'Inter', sans-serif",
    overflow: 'hidden',
  },
  sidebar: {
    width: '260px',
    backgroundColor: '#111827',
    borderRight: '1px solid rgba(255, 255, 255, 0.07)',
    display: 'flex',
    flexDirection: 'column',
    padding: '24px 16px',
    flexShrink: 0,
  },
  logoArea: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '40px',
    paddingLeft: '8px',
  },
  logoIcon: {
    width: '36px',
    height: '36px',
    background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
    borderRadius: '8px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  logoText: {
    fontSize: '1.2rem',
    fontWeight: 700,
    background: 'linear-gradient(to right, #ffffff, #d8b4fe)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  navLinks: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    flexGrow: 1,
  },
  navItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '12px 16px',
    color: '#9ca3af',
    textDecoration: 'none',
    fontSize: '0.95rem',
    fontWeight: 500,
    borderRadius: '8px',
    transition: 'all 0.2s ease',
  },
  navItemActive: {
    color: '#f3f4f6',
    backgroundColor: 'rgba(59, 130, 246, 0.15)',
    borderLeft: '3px solid #3b82f6',
    paddingLeft: '13px',
  },
  sidebarFooter: {
    paddingTop: '16px',
    borderTop: '1px solid rgba(255, 255, 255, 0.05)',
  },
  logoutBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    width: '100%',
    padding: '12px 16px',
    backgroundColor: 'transparent',
    border: 'none',
    color: '#9ca3af',
    fontSize: '0.95rem',
    cursor: 'pointer',
    textAlign: 'left',
    borderRadius: '8px',
  },
  mainPane: {
    flexGrow: 1,
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    overflow: 'hidden',
  },
  header: {
    height: '70px',
    borderBottom: '1px solid rgba(255, 255, 255, 0.07)',
    padding: '0 24px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#0d1321',
  },
  userBadge: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
  },
  avatar: {
    width: '32px',
    height: '32px',
    borderRadius: '50%',
    backgroundColor: 'rgba(59, 130, 246, 0.2)',
    border: '1px solid #3b82f6',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#3b82f6',
    fontWeight: 600,
  },
  contentArea: {
    flexGrow: 1,
    padding: '24px',
    overflowY: 'auto',
  },
};

export default Layout;
