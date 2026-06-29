import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { Database, AlertTriangle, Cpu, ArrowRight, RefreshCw, CheckCircle, XCircle, Clock } from 'lucide-react';

interface RecentRun {
  id: string;
  status: string;
  records_synced: number;
  started_at: string;
  completed_at: string | null;
  error: string | null;
}

interface StatsData {
  connections: number;
  schemas: number;
  tables: number;
  columns: number;
  health_index: string;
  recent_runs: RecentRun[];
}

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [connections, setConnections] = useState<any[]>([]);
  const [stats, setStats] = useState<StatsData>({
    connections: 0,
    schemas: 0,
    tables: 0,
    columns: 0,
    health_index: '100%',
    recent_runs: []
  });
  
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncError, setSyncError] = useState('');

  // Fetch connections and stats on mount
  useEffect(() => {
    fetchInitialData();
  }, []);

  // Poll stats while job is running in background
  useEffect(() => {
    let intervalId: any;
    const isRunning = stats.recent_runs.some(run => run.status === 'RUNNING');
    
    if (isRunning) {
      setSyncing(true);
      intervalId = setInterval(() => {
        refreshStats();
      }, 3000);
    } else {
      setSyncing(false);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [stats.recent_runs]);

  const fetchInitialData = async () => {
    setLoading(true);
    try {
      const connData = await api.get('/config/connection');
      setConnections(connData);
      const statsData = await api.get('/sync/stats');
      setStats(statsData);
    } catch (err) {
      console.error('Error fetching dashboard datasets:', err);
    } finally {
      setLoading(false);
    }
  };

  const refreshStats = async () => {
    try {
      const statsData = await api.get('/sync/stats');
      setStats(statsData);
    } catch (err) {
      console.error('Error refreshing system statistics:', err);
    }
  };

  const handleTriggerSync = async () => {
    if (connections.length === 0) return;
    
    setSyncError('');
    setSyncing(true);
    const targetDbId = connections[0].id; // Trigger sync on the first connection profile

    try {
      await api.post(`/sync/trigger?database_id=${targetDbId}`);
      // Refresh statistics to load the RUNNING job state and trigger polling loop
      refreshStats();
    } catch (err: any) {
      setSyncing(false);
      setSyncError(err.message || 'Failed to start synchronization.');
    }
  };

  const metrics = [
    { title: 'Global Health Index', value: stats.health_index, sub: 'Average synchronization success', icon: <Cpu color="#10b981" /> },
    { title: 'Connected Database Profiles', value: stats.connections.toString(), sub: 'Configured data platforms', icon: <Database color="#3b82f6" /> },
    { title: 'Ingested Tables', value: stats.tables.toString(), sub: 'Active tables in schema graph', icon: <Database color="#a78bfa" /> },
    { title: 'Ingested Columns', value: stats.columns.toString(), sub: 'Tracked field dependencies', icon: <Database color="#fb7185" /> },
  ];

  const formatTime = (isoString: string) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch (e) {
      return isoString;
    }
  };

  return (
    <div style={styles.container}>
      {/* Metrics Row */}
      <section style={styles.metricsGrid}>
        {metrics.map((m) => (
          <div key={m.title} style={styles.card}>
            <div style={styles.cardHeader}>
              <span style={styles.cardTitle}>{m.title}</span>
              <div style={styles.cardIcon}>{m.icon}</div>
            </div>
            <div style={styles.cardValue}>{m.value}</div>
            <span style={styles.cardSub}>{m.sub}</span>
          </div>
        ))}
      </section>

      {/* Connection setup prompts or actions */}
      {connections.length === 0 && !loading ? (
        <section style={styles.warningPanel}>
          <div style={styles.warningHeader}>
            <AlertTriangle size={24} color="#f59e0b" />
            <h3>No Active Data Connection Profile Configured</h3>
          </div>
          <p style={styles.panelText}>
            ImpactGraph requires credentials configuration to connect to your Snowflake workspace and extract catalog mappings. 
            Navigate to settings to build your profile.
          </p>
          <button onClick={() => navigate('/settings')} style={styles.btnAction}>
            <span>Set Up Snowflake Connector</span>
            <ArrowRight size={18} />
          </button>
        </section>
      ) : (
        <section style={styles.actionPanel}>
          <div style={styles.actionHeader}>
            <div>
              <h3 style={styles.panelTitle}>Ingestion Control Hub</h3>
              <p style={styles.panelText}>
                Trigger catalog sync runs to fetch databases structural metadata, views SQL code, and role privilege maps.
              </p>
            </div>
            
            <button 
              onClick={handleTriggerSync} 
              disabled={syncing || loading} 
              style={{
                ...styles.btnTrigger,
                ...((syncing || loading) ? styles.btnTriggerDisabled : {})
              }}
            >
              <RefreshCw size={18} style={syncing ? styles.spinAnimation : {}} />
              <span>{syncing ? 'Extracting Metadata...' : 'Trigger Database Sync'}</span>
            </button>
          </div>

          {syncError && <div style={styles.errorText}>{syncError}</div>}

          {/* Sync Jobs history audit list */}
          <div style={styles.historySection}>
            <h4 style={styles.historyTitle}>Recent Sync Operations</h4>
            <div style={styles.tableWrapper}>
              <table style={styles.table}>
                <thead>
                  <tr style={styles.thRow}>
                    <th style={styles.th}>Job ID</th>
                    <th style={styles.th}>Started At</th>
                    <th style={styles.th}>Completed At</th>
                    <th style={styles.th}>Objects Synced</th>
                    <th style={styles.th}>Status</th>
                    <th style={styles.th}>Logs / Messages</th>
                  </tr>
                </thead>
                <tbody>
                  {stats.recent_runs.length === 0 ? (
                    <tr>
                      <td colSpan={6} style={styles.tdEmpty}>No synchronization runs recorded yet. Click the trigger button above to crawl your catalog schema.</td>
                    </tr>
                  ) : (
                    stats.recent_runs.map((run) => (
                      <tr key={run.id} style={styles.tr}>
                        <td style={styles.tdId}>{run.id.substring(0, 8)}...</td>
                        <td style={styles.td}>{formatTime(run.started_at)}</td>
                        <td style={styles.td}>{run.completed_at ? formatTime(run.completed_at) : '--'}</td>
                        <td style={styles.td}>{run.records_synced} items</td>
                        <td style={styles.td}>
                          <span style={{
                            ...styles.statusBadge,
                            ...(run.status === 'SUCCESS' ? styles.badgeSuccess : 
                              run.status === 'FAILED' ? styles.badgeFailed : styles.badgeRunning)
                          }}>
                            {run.status === 'SUCCESS' && <CheckCircle size={12} />}
                            {run.status === 'FAILED' && <XCircle size={12} />}
                            {run.status === 'RUNNING' && <Clock size={12} />}
                            <span>{run.status}</span>
                          </span>
                        </td>
                        <td style={{
                          ...styles.tdError,
                          ...(run.error ? styles.textDanger : {})
                        }}>
                          {run.error || 'Job completed successfully.'}
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      )}
    </div>
  );
};

// CSS Styles
const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
  },
  metricsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
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
  warningPanel: {
    padding: '28px',
    backgroundColor: 'rgba(245, 158, 11, 0.02)',
    border: '1px solid rgba(245, 158, 11, 0.12)',
    borderRadius: '12px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  warningHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    color: '#f59e0b',
  },
  actionPanel: {
    padding: '28px',
    backgroundColor: '#111827',
    border: '1px solid rgba(255, 255, 255, 0.07)',
    borderRadius: '12px',
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
  },
  actionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: '20px',
  },
  panelTitle: {
    fontSize: '1.2rem',
    fontWeight: 600,
    color: '#ffffff',
    marginBottom: '4px',
  },
  panelText: {
    fontSize: '0.9rem',
    color: '#9ca3af',
    lineHeight: '1.5',
    maxWidth: '700px',
  },
  btnAction: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    padding: '12px 20px',
    backgroundColor: '#3b82f6',
    border: 'none',
    color: 'white',
    fontSize: '0.875rem',
    fontWeight: 600,
    borderRadius: '8px',
    cursor: 'pointer',
    width: 'fit-content',
  },
  btnTrigger: {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '10px',
    padding: '12px 24px',
    background: 'linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%)',
    border: 'none',
    color: 'white',
    fontSize: '0.9rem',
    fontWeight: 600,
    borderRadius: '8px',
    cursor: 'pointer',
    boxShadow: '0 4px 12px rgba(139, 92, 246, 0.25)',
  },
  btnTriggerDisabled: {
    opacity: 0.6,
    cursor: 'not-allowed',
    boxShadow: 'none',
  },
  errorText: {
    color: '#ef4444',
    fontSize: '0.85rem',
    backgroundColor: 'rgba(239, 68, 68, 0.05)',
    padding: '10px 14px',
    border: '1px solid rgba(239, 68, 68, 0.15)',
    borderRadius: '6px',
  },
  historySection: {
    borderTop: '1px solid rgba(255, 255, 255, 0.06)',
    paddingTop: '24px',
  },
  historyTitle: {
    fontSize: '1rem',
    fontWeight: 600,
    color: '#ffffff',
    marginBottom: '16px',
  },
  tableWrapper: {
    overflowX: 'auto',
    borderRadius: '8px',
    border: '1px solid rgba(255, 255, 255, 0.05)',
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    textAlign: 'left',
    backgroundColor: 'rgba(255, 255, 255, 0.01)',
  },
  thRow: {
    backgroundColor: 'rgba(255, 255, 255, 0.02)',
    borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
  },
  th: {
    padding: '14px 18px',
    fontSize: '0.8rem',
    fontWeight: 600,
    textTransform: 'uppercase',
    color: '#9ca3af',
  },
  tr: {
    borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
  },
  td: {
    padding: '14px 18px',
    fontSize: '0.85rem',
    color: '#f3f4f6',
  },
  tdId: {
    padding: '14px 18px',
    fontSize: '0.85rem',
    fontFamily: 'monospace',
    color: '#6b7280',
  },
  tdEmpty: {
    padding: '36px 18px',
    fontSize: '0.85rem',
    color: '#6b7280',
    textAlign: 'center',
  },
  tdError: {
    padding: '14px 18px',
    fontSize: '0.8rem',
    color: '#9ca3af',
    maxWidth: '240px',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  textDanger: {
    color: '#ef4444',
  },
  statusBadge: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    padding: '4px 10px',
    borderRadius: '9999px',
    fontSize: '0.75rem',
    fontWeight: 600,
    textTransform: 'uppercase',
    letterSpacing: '0.03em',
  },
  badgeSuccess: {
    backgroundColor: 'rgba(16, 185, 129, 0.08)',
    color: '#10b981',
    border: '1px solid rgba(16, 185, 129, 0.2)',
  },
  badgeFailed: {
    backgroundColor: 'rgba(239, 68, 68, 0.08)',
    color: '#ef4444',
    border: '1px solid rgba(239, 68, 68, 0.2)',
  },
  badgeRunning: {
    backgroundColor: 'rgba(59, 130, 246, 0.08)',
    color: '#3b82f6',
    border: '1px solid rgba(59, 130, 246, 0.2)',
  },
  spinAnimation: {
    animation: 'spin 1.5s linear infinite',
  },
};

// Add standard spinning keyframe style via browser inject
const styleTag = document.createElement("style");
styleTag.innerHTML = `
  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }
`;
document.head.appendChild(styleTag);

export default Dashboard;
