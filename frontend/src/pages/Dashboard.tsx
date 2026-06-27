import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Database, AlertTriangle, Cpu, ArrowRight } from 'lucide-react';

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [connections, setConnections] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch active connections list on startup
    api.get('/config/connection')
      .then((data) => setConnections(data))
      .catch((err) => console.error('Failed to load connections:', err))
      .finally(() => setLoading(false));
  }, []);

  const stats = [
    { title: 'Global Health Index', value: '100%', sub: 'No critical failures detected', icon: <Cpu color="#10b981" /> },
    { title: 'Connected Warehouses', value: loading ? '...' : connections.length.toString(), sub: 'Active source databases', icon: <Database color="#3b82f6" /> },
    { title: 'Downstream Risk Incidents', value: '0', sub: 'High risk schema modifications', icon: <AlertTriangle color="#f59e0b" /> },
  ];

  return (
    <div style={styles.container}>
      {/* Overview Cards Grid */}
      <section style={styles.metricsGrid}>
        {stats.map((stat) => (
          <div key={stat.title} style={styles.card}>
            <div style={styles.cardHeader}>
              <span style={styles.cardTitle}>{stat.title}</span>
              <div style={styles.cardIcon}>{stat.icon}</div>
            </div>
            <div style={styles.cardValue}>{stat.value}</div>
            <span style={styles.cardSub}>{stat.sub}</span>
          </div>
        ))}
      </section>

      {/* Primary Landing Promo Panel */}
      <section style={styles.infoPanel}>
        <h3 style={styles.panelTitle}>Welcome to ImpactGraph</h3>
        <p style={styles.panelText}>
          ImpactGraph is your central control center for tracking schema mutations, tracing data dependency trees, 
          and auditing organizational access security.
        </p>

        {connections.length === 0 && !loading ? (
          <div style={styles.setupWarningCard}>
            <div style={styles.warningHeader}>
              <AlertTriangle size={24} color="#f59e0b" />
              <h4>No Active Data Connections Found</h4>
            </div>
            <p style={styles.warningText}>
              Before you can audit column lineage, compute blast-radius risks, or browse role privileges, you must 
              configure a connection to your Snowflake data platform in the configuration settings workspace.
            </p>
            <button onClick={() => navigate('/settings')} style={styles.btnAction}>
              <span>Set Up Snowflake Connector</span>
              <ArrowRight size={18} />
            </button>
          </div>
        ) : (
          <div style={styles.successCard}>
            <h4>Connection Configured</h4>
            <p>
              Your Snowflake connector database profile is configured. Subsequent specs will implement the background 
              job extraction syncer, metadata AST view parser, trigram indexing explorer, and React Flow visualizers.
            </p>
          </div>
        )}
      </section>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
  },
  metricsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '20px',
  },
  card: {
    padding: '24px',
    backgroundColor: '#111827',
    border: '1px solid rgba(255, 255, 255, 0.07)',
    borderRadius: '12px',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  cardTitle: {
    fontSize: '0.85rem',
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    color: '#9ca3af',
  },
  cardIcon: {
    width: '36px',
    height: '36px',
    borderRadius: '8px',
    backgroundColor: 'rgba(255, 255, 255, 0.02)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  cardValue: {
    fontSize: '2rem',
    fontWeight: 700,
    fontFamily: "'Outfit', sans-serif",
    color: '#ffffff',
  },
  cardSub: {
    fontSize: '0.75rem',
    color: '#6b7280',
  },
  infoPanel: {
    padding: '28px',
    backgroundColor: '#111827',
    border: '1px solid rgba(255, 255, 255, 0.07)',
    borderRadius: '12px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  panelTitle: {
    fontSize: '1.25rem',
    fontWeight: 600,
    color: '#ffffff',
  },
  panelText: {
    fontSize: '0.9rem',
    color: '#9ca3af',
    lineHeight: '1.5',
    maxWidth: '800px',
  },
  setupWarningCard: {
    marginTop: '20px',
    padding: '24px',
    backgroundColor: 'rgba(245, 158, 11, 0.03)',
    border: '1px solid rgba(245, 158, 11, 0.15)',
    borderRadius: '8px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    maxWidth: '650px',
  },
  warningHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    color: '#f59e0b',
  },
  warningText: {
    fontSize: '0.85rem',
    color: '#9ca3af',
    lineHeight: '1.5',
  },
  btnAction: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    padding: '10px 18px',
    backgroundColor: '#3b82f6',
    border: 'none',
    color: 'white',
    fontSize: '0.85rem',
    fontWeight: 600,
    borderRadius: '6px',
    cursor: 'pointer',
    width: 'fit-content',
    transition: 'background-color 0.2s',
  },
  successCard: {
    marginTop: '20px',
    padding: '24px',
    backgroundColor: 'rgba(16, 185, 129, 0.03)',
    border: '1px solid rgba(16, 185, 129, 0.15)',
    borderRadius: '8px',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    maxWidth: '650px',
    color: '#10b981',
  },
};

export default Dashboard;
