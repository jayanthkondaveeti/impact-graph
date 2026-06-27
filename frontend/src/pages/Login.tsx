import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { ShieldAlert } from 'lucide-react';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Format body as x-www-form-urlencoded to match FastAPI OAuth2 dependencies
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);

    try {
      const data = await api.post('/auth/login', params);
      localStorage.setItem('access_token', data.access_token);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <div style={styles.header}>
          <div style={styles.logoIcon}>
            <ShieldAlert size={24} color="white" />
          </div>
          <h1 style={styles.title}>ImpactGraph</h1>
          <p style={styles.subtitle}>Enter credentials to access the data catalog portal</p>
        </div>

        {error && <div style={styles.errorBanner}>{error}</div>}

        <form onSubmit={handleSubmit} style={styles.form}>
          <div style={styles.formGroup}>
            <label style={styles.label}>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={styles.input}
              placeholder="e.g., admin"
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

          <button type="submit" disabled={loading} style={styles.submitBtn}>
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
};

const styles: Record<string, React.CSSProperties> = {
  container: {
    display: 'flex',
    height: '100vh',
    width: '100vw',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#0a0e1a',
    fontFamily: "'Inter', sans-serif",
  },
  card: {
    width: '400px',
    padding: '32px',
    backgroundColor: '#111827',
    border: '1px solid rgba(255, 255, 255, 0.07)',
    borderRadius: '12px',
    boxShadow: '0 10px 25px rgba(0, 0, 0, 0.4)',
  },
  header: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    marginBottom: '28px',
  },
  logoIcon: {
    width: '48px',
    height: '48px',
    background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)',
    borderRadius: '12px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: '16px',
    boxShadow: '0 0 15px rgba(139, 92, 246, 0.3)',
  },
  title: {
    fontSize: '1.6rem',
    fontWeight: 700,
    fontFamily: "'Outfit', sans-serif",
    marginBottom: '4px',
    color: '#ffffff',
  },
  subtitle: {
    fontSize: '0.85rem',
    color: '#9ca3af',
    textAlign: 'center',
  },
  errorBanner: {
    backgroundColor: 'rgba(239, 68, 68, 0.1)',
    border: '1px solid rgba(239, 68, 68, 0.2)',
    color: '#ef4444',
    padding: '10px 14px',
    borderRadius: '6px',
    fontSize: '0.85rem',
    marginBottom: '20px',
    textAlign: 'center',
  },
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '20px',
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
  submitBtn: {
    marginTop: '10px',
    background: 'linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%)',
    border: 'none',
    color: 'white',
    padding: '12px',
    borderRadius: '8px',
    fontSize: '0.95rem',
    fontWeight: 600,
    cursor: 'pointer',
    transition: 'opacity 0.2s',
  },
};

export default Login;
