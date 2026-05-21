import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useScrapeProgress } from '../hooks/useScrapeProgress';
import api from '../api/client';

function Profile() {
  const { user } = useAuth();
  const { progress, stage, message, isActive, error, startScrape } = useScrapeProgress();

  const [credStatus, setCredStatus] = useState(null);
  const [birdiesEmail, setBirdiesEmail] = useState('');
  const [birdiesPassword, setBirdiesPassword] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  useEffect(() => {
    api.get('/profile/credentials')
      .then(res => {
        setCredStatus(res);
        if (res?.username) {
          setBirdiesEmail(res.username);
        }
      })
      .catch(err => console.error(err));
  }, []);

  useEffect(() => {
    if (!isActive && progress === 100) {
      api.get('/profile/credentials')
        .then(res => {
          setCredStatus(res);
          if (res?.username) {
            setBirdiesEmail(res.username);
          }
        })
        .catch(err => console.error(err));
    }
  }, [isActive, progress]);

  const formatLastRefreshed = (dateStr) => {
    if (!dateStr) return '';
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return '';
    return d.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  };

  const handleSaveCredentials = async () => {
    setIsSaving(true);
    setSaveMessage('');
    try {
      const payload = { username: birdiesEmail };
      if (birdiesPassword) {
        payload.password = birdiesPassword;
      }
      const res = await api.put('/profile/credentials', payload);
      setCredStatus(res);
      setSaveMessage('Credentials saved successfully!');
      setBirdiesPassword(''); // Clear password field after saving for security
    } catch (err) {
      setSaveMessage(err.message || 'Failed to save credentials');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDisconnect = async () => {
    setIsSaving(true);
    setSaveMessage('');
    try {
      await api.delete('/profile/credentials');
      setCredStatus({ has_credentials: false, username: null });
      setBirdiesEmail('');
      setBirdiesPassword('');
      setSaveMessage('Credentials disconnected successfully!');
    } catch (err) {
      setSaveMessage(err.message || 'Failed to disconnect credentials');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="page">
      <div className="section-header">
        <div className="section-title">
          <span className="section-title-icon">👤</span>
          <h2>Profile</h2>
        </div>
      </div>

      <div className="grid-2" style={{ alignItems: 'start' }}>
        {/* Left Column */}
        <div className="stagger-children" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
          {/* My Profile Card */}
          <div className="glass-card">
            <div className="flex-between" style={{ marginBottom: 'var(--space-lg)' }}>
              <h3>My Profile</h3>
              <button className="btn-secondary btn-sm">Edit</button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-lg)' }}>
              <div className="avatar avatar-xl">
                {user?.display_name
                  ? user.display_name
                      .split(' ')
                      .map((w) => w[0])
                      .join('')
                      .toUpperCase()
                      .slice(0, 2)
                  : '?'}
              </div>
              <div>
                <h3 style={{ marginBottom: 'var(--space-xs)' }}>
                  {user?.display_name || 'Golfer'}
                </h3>
                <p className="text-muted" style={{ fontSize: 'var(--font-sm)' }}>
                  {user?.email || 'email@example.com'}
                </p>
                <div style={{ marginTop: 'var(--space-sm)', display: 'flex', gap: 'var(--space-sm)' }}>
                  <span className="badge badge-emerald">Active</span>
                  {user?.is_admin && <span className="badge badge-gold">Admin</span>}
                </div>
              </div>
            </div>

            <div className="divider" />

            <div className="grid-3" style={{ textAlign: 'center' }}>
              <div>
                <div style={{ fontSize: 'var(--font-2xl)', fontWeight: 700, color: 'var(--accent-emerald)' }}>
                  —
                </div>
                <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-muted)', marginTop: 4 }}>
                  Rounds
                </div>
              </div>
              <div>
                <div style={{ fontSize: 'var(--font-2xl)', fontWeight: 700, color: 'var(--accent-gold)' }}>
                  —
                </div>
                <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-muted)', marginTop: 4 }}>
                  Avg Score
                </div>
              </div>
              <div>
                <div style={{ fontSize: 'var(--font-2xl)', fontWeight: 700 }}>
                  —
                </div>
                <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-muted)', marginTop: 4 }}>
                  Handicap
                </div>
              </div>
            </div>
          </div>

          {/* 18Birdies Connection */}
          <div className="glass-card">
            <div className="flex-between" style={{ marginBottom: 'var(--space-lg)' }}>
              <h3>18Birdies Connection</h3>
              {credStatus?.has_credentials ? (
                <span className="badge badge-emerald">Connected</span>
              ) : (
                <span className="badge badge-neutral">Not Connected</span>
              )}
            </div>

            <p className="text-secondary" style={{ fontSize: 'var(--font-sm)', marginBottom: 'var(--space-lg)' }}>
              Link your 18Birdies account to automatically import your rounds and stats.
            </p>

            {saveMessage && (
              <div style={{ 
                marginBottom: 'var(--space-md)', 
                padding: 'var(--space-sm)',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: saveMessage.includes('success') ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                border: `1px solid ${saveMessage.includes('success') ? 'var(--accent-emerald)' : 'var(--accent-ruby)'}`,
                fontSize: 'var(--font-sm)', 
                color: saveMessage.includes('success') ? 'var(--accent-emerald)' : 'var(--accent-ruby)' 
              }}>
                {saveMessage}
              </div>
            )}

            <div className="auth-form">
              <div className="input-group">
                <label className="input-label" htmlFor="birdies-email">
                  18Birdies Email
                </label>
                <input
                  id="birdies-email"
                  type="email"
                  className="input-field"
                  placeholder="your-email@18birdies.com"
                  value={birdiesEmail}
                  onChange={(e) => setBirdiesEmail(e.target.value)}
                />
              </div>
              <div className="input-group">
                <label className="input-label" htmlFor="birdies-password">
                  18Birdies Password
                </label>
                <input
                  id="birdies-password"
                  type="password"
                  className="input-field"
                  placeholder={credStatus?.has_credentials ? "•••••••• (Saved)" : "••••••••"}
                  value={birdiesPassword}
                  onChange={(e) => setBirdiesPassword(e.target.value)}
                />
              </div>
              <div style={{ display: 'flex', gap: 'var(--space-sm)' }}>
                <button 
                  className="btn-secondary" 
                  onClick={handleSaveCredentials}
                  disabled={isSaving || !birdiesEmail || (!birdiesPassword && !credStatus?.has_credentials)}
                >
                  {isSaving ? 'Saving...' : 'Save Credentials'}
                </button>
                {credStatus?.has_credentials && (
                  <button 
                    className="btn-danger" 
                    onClick={handleDisconnect}
                    disabled={isSaving}
                    style={{ backgroundColor: 'var(--accent-ruby)', color: 'white', border: 'none' }}
                  >
                    Disconnect
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="stagger-children" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
          {/* Refresh Data Card */}
          <div className="glass-card">
            <h3 style={{ marginBottom: 'var(--space-sm)' }}>Refresh Data</h3>
            <p
              className="text-secondary"
              style={{ fontSize: 'var(--font-sm)', marginBottom: 'var(--space-lg)' }}
            >
              Pull the latest rounds from your linked 18Birdies account. This may take a minute.
            </p>

            {error && (
              <div className="auth-error" style={{ marginBottom: 'var(--space-md)' }}>
                {error}
              </div>
            )}

            {isActive && (
              <div style={{ marginBottom: 'var(--space-lg)' }}>
                <div className="flex-between" style={{ marginBottom: 'var(--space-sm)' }}>
                  <span
                    style={{
                      fontSize: 'var(--font-sm)',
                      fontWeight: 500,
                      color: 'var(--text-secondary)',
                    }}
                  >
                    {stage}
                  </span>
                  <span className="progress-text">{Math.round(progress)}%</span>
                </div>
                <div className="progress-bar-container progress-bar-lg">
                  <div
                    className="progress-bar-fill"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <p
                  style={{
                    fontSize: 'var(--font-xs)',
                    color: 'var(--text-muted)',
                    marginTop: 'var(--space-sm)',
                  }}
                >
                  {message}
                </p>
              </div>
            )}

            <button
              className="btn-primary btn-lg glow"
              style={{ width: '100%' }}
              onClick={startScrape}
              disabled={isActive}
            >
              {isActive ? (
                <>
                  <span className="spinner" />
                  Refreshing...
                </>
              ) : (
                <>🔄 Refresh Data</>
              )}
            </button>

            {credStatus?.last_scraped_at && (
              <p style={{
                fontSize: 'var(--font-xs)',
                color: 'var(--text-muted)',
                textAlign: 'center',
                marginTop: 'var(--space-sm)'
              }}>
                Last Refreshed: {formatLastRefreshed(credStatus.last_scraped_at)}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Profile;
