import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Server, ShieldCheck, AlertCircle } from 'lucide-react';

const Settings: React.FC = () => {
  const [connections, setConnections] = useState<any[]>([]);
  const [name, setName] = useState('');
  const [account, setAccount] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [warehouse, setWarehouse] = useState('');
  
  const [status, setStatus] = useState({ type: '', message: '' });
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    loadConnections();
  }, []);

  const loadConnections = async () => {
    try {
      const data = await api.get('/config/connection');
      setConnections(data);
    } catch (err) {
      console.error('Failed to load connections:', err);
    }
  };

  const getPayload = () => ({
    name,
    platform: 'snowflake',
    config: {
      account,
      username,
      password,
      warehouse,
    }
  });

  const handleTest = async () => {
    setStatus({ type: '', message: '' });
    setTesting(true);
    try {
      const data = await api.post('/config/connection/test', {
        platform: 'snowflake',
        config: { account, username, warehouse } // send non-sensitive variables for verification handshake
      });
      setStatus({ type: 'success', message: data.message });
    } catch (err: any) {
      setStatus({ type: 'error', message: err.message || 'Connection test failed.' });
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus({ type: '', message: '' });
    setSaving(true);
    try {
      await api.post('/config/connection', getPayload());
      setStatus({ type: 'success', message: 'Connection properties encrypted and saved successfully.' });
      setName('');
      setAccount('');
      setUsername('');
      setPassword('');
      setWarehouse('');
      loadConnections();
    } catch (err: any) {
      setStatus({ type: 'error', message: err.message || 'Saving configuration failed.' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.grid}>
        {/* Left Side: Connection Input Form */}
        <div style={styles.card}>
          <h3 style={styles.cardTitle}>Add Snowflake Database Connection</h3>
          <p style={styles.cardDesc}>Connection details are encrypted at rest using AES-256 keys.</p>

          {status.message && (
            <div style={{
              ...styles.statusBanner,
              ...(status.type === 'success' ? styles.statusSuccess : styles.statusError)
            }}>
              {status.type === 'success' ? <ShieldCheck size={18} /> : <AlertCircle size={18} />}
              <span>{status.message}</span>
            </div>
          )}

          <form onSubmit={handleSave} style={styles.form}>
            <div style={styles.formGroup}>
              <label style={styles.label}>Connection Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                style={styles.input}
                placeholder="e.g., snowflake_production"
                required
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Snowflake Account Identifier</label>
              <input
                type="text"
                value={account}
                onChange={(e) => setAccount(e.target.value)}
                style={styles.input}
                placeholder="e.g., xy12345.us-east-1"
                required
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Warehouse Name</label>
              <input
                type="text"
                value={warehouse}
                onChange={(e) => setWarehouse(e.target.value)}
                style={styles.input}
                placeholder="e.g., COMPUTE_WH"
                required
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                style={styles.input}
                placeholder="e.g., INGEST_USER"
                required
              />
            </div>

            <div style={styles.formGroup}>
              <label style={styles.label}>Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                style={styles.input}
                placeholder="••••••••"
                required
              />
            </div>

            <div style={styles.actionButtons}>
              <button 
                type="button" 
                onClick={handleTest} 
                disabled={testing || saving || !account || !username || !warehouse}
                style={styles.btnSecondary}
              >
                {testing ? 'Testing...' : 'Test Connection'}
              </button>
              <button 
                type="submit" 
                disabled={saving || testing}
                style={styles.btnPrimary}
              >
                {saving ? 'Saving...' : 'Save Configuration'}
              </button>
            </div>
          </form>
        </div>

        {/* Right Side: Active Connections List */}
        <div style={styles.card}>
          <h3 style={styles.cardTitle}>Active Connection Profiles</h3>
          <p style={styles.cardDesc}>Connected credentials and platform hooks configured.</p>

          <div style={styles.connectionsList}>
            {connections.length === 0 ? (
              <div style={styles.emptyState}>
                <Server size={32} color="#6b7280" />
                <p>No active database connections defined yet.</p>
              </div>
            ) : (
              connections.map((conn) => (
                <div key={conn.id} style={styles.connectionItem}>
                  <div style={styles.connectionInfo}>
                    <div style={styles.dbIcon}>
                      <Server size={18} color="#3b82f6" />
                    </div>
                    <div style={styles.dbDetails}>
                      <span style={styles.dbName}>{conn.name}</span>
                      <span style={styles.dbPlatform}>Platform: {conn.platform}</span>
                    </div>
                  </div>
                  <div style={styles.badgeSuccess}>Encrypted</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))',
    gap: '24px',
    alignItems: 'start',
  },
  card: {
    padding: '28px',
    backgroundColor: '#111827',
    border: '1px solid rgba(255, 255, 255, 0.07)',
    borderRadius: '12px',
  },
  cardTitle: {
    fontSize: '1.1rem',
    fontWeight: 600,
    color: '#ffffff',
    marginBottom: '4px',
  },
  cardDesc: {
    fontSize: '0.8rem',
    color: '#9ca3af',
    marginBottom: '24px',
  },
  statusBanner: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '12px 16px',
    borderRadius: '8px',
    fontSize: '0.85rem',
    marginBottom: '20px',
    lineHeight: '1.4',
  },
  statusSuccess: {
    backgroundColor: 'rgba(16, 185, 129, 0.08)',
    border: '1px solid rgba(16, 185, 129, 0.2)',
    color: '#10b981',
  },
  statusError: {
    backgroundColor: 'rgba(239, 68, 68, 0.08)',
    border: '1px solid rgba(239, 68, 68, 0.2)',
    color: '#ef4444',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  formGroup: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
  },
  label: {
    fontSize: '0.85rem',
    fontWeight: 600,
    color: '#9ca3af',
  },
  input: {
    backgroundColor: 'rgba(255, 255, 255, 0.03)',
    border: '1px solid rgba(255, 255, 255, 0.08)',
    borderRadius: '8px',
    padding: '10px 14px',
    color: '#f3f4f6',
    fontSize: '0.9rem',
    outline: 'none',
    transition: 'border-color 0.2s',
  },
  actionButtons: {
    display: 'flex',
    gap: '12px',
    marginTop: '12px',
  },
  btnPrimary: {
    flexGrow: 1,
    backgroundColor: '#3b82f6',
    border: 'none',
    color: 'white',
    padding: '12px',
    borderRadius: '8px',
    fontSize: '0.875rem',
    fontWeight: 600,
    cursor: 'pointer',
    textAlign: 'center',
    transition: 'background-color 0.2s',
  },
  btnSecondary: {
    backgroundColor: 'rgba(255, 255, 255, 0.04)',
    border: '1px solid rgba(255, 255, 255, 0.08)',
    color: '#f3f4f6',
    padding: '12px 18px',
    borderRadius: '8px',
    fontSize: '0.875rem',
    fontWeight: 600,
    cursor: 'pointer',
    textAlign: 'center',
  },
  connectionsList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  emptyState: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '12px',
    padding: '48px 0',
    color: '#6b7280',
    fontSize: '0.85rem',
  },
  connectionItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '14px 18px',
    backgroundColor: 'rgba(255, 255, 255, 0.02)',
    border: '1px solid rgba(255, 255, 255, 0.05)',
    borderRadius: '8px',
  },
  connectionInfo: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  dbIcon: {
    width: '32px',
    height: '32px',
    borderRadius: '6px',
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  dbDetails: {
    display: 'flex',
    flexDirection: 'column',
    gap: '2px',
  },
  dbName: {
    fontSize: '0.9rem',
    fontWeight: 600,
    color: '#ffffff',
  },
  dbPlatform: {
    fontSize: '0.75rem',
    color: '#6b7280',
  },
  badgeSuccess: {
    fontSize: '0.7rem',
    fontWeight: 700,
    color: '#10b981',
    backgroundColor: 'rgba(16, 185, 129, 0.1)',
    border: '1px solid rgba(16, 185, 129, 0.2)',
    padding: '4px 8px',
    borderRadius: '9999px',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
  },
};

export default Settings;
