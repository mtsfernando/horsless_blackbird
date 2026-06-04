import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useScrapeProgress } from '../hooks/useScrapeProgress';
import api from '../api/client';

const GOLFER_AVATARS = [
  { id: 'tiger', name: 'The Big Cat', golfer: 'Tiger Woods', emoji: '🐅' },
  { id: 'lefty', name: "Lefty's Thumb", golfer: 'Phil Mickelson', emoji: '👍' },
  { id: 'arnie', name: 'The Sweet Tea', golfer: 'Arnold Palmer', emoji: '🍹' },
  { id: 'bear', name: 'The Golden Bear', golfer: 'Jack Nicklaus', emoji: '🐻' },
  { id: 'scientist', name: 'The Golf Scientist', golfer: 'Bryson DeChambeau', emoji: '🧪' },
  { id: 'wild', name: 'Wild Thing', golfer: 'John Daly', emoji: '🍺' },
  { id: 'climber', name: 'The Tree Climber', golfer: 'Sergio Garcia', emoji: '🌳' },
  { id: 'gymbro', name: 'The Gym Bro', golfer: 'Brooks Koepka', emoji: '😒' },
  { id: 'shamrock', name: "Rory's Shamrock", golfer: 'Rory McIlroy', emoji: '☘️' },
  { id: 'queen', name: 'LPGA Queen', golfer: 'Nelly Korda', emoji: '👑' }
];

function Profile() {
  const { user } = useAuth();
  const { progress, stage, message, isActive, error, startScrape } = useScrapeProgress();

  const [credStatus, setCredStatus] = useState(null);
  const [birdiesEmail, setBirdiesEmail] = useState('');
  const [birdiesPassword, setBirdiesPassword] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  // Player profile & stats states
  const [profileData, setProfileData] = useState(null);
  const [playerStats, setPlayerStats] = useState({ rounds: '—', avgScore: '—', handicap: '—' });
  const [showAvatarSelector, setShowAvatarSelector] = useState(false);
  const [hoveredAvatar, setHoveredAvatar] = useState(null);

  const fetchProfileAndStats = async () => {
    try {
      const profile = await api.get('/profile');
      setProfileData(profile);
      const lead = await api.get('/leaderboard');
      const pStats = lead.find(p => p.player_id === profile.id);
      if (pStats) {
        setPlayerStats({
          rounds: pStats.rounds_played ?? '—',
          avgScore: pStats.avg_score ? Math.round(pStats.avg_score) : '—',
          handicap: pStats.avg_score ? ((pStats.avg_score - 72) * 0.96).toFixed(1) : '—'
        });
      }
    } catch (err) {
      console.error('Error fetching profile or stats:', err);
    }
  };

  useEffect(() => {
    api.get('/profile/credentials')
      .then(res => {
        setCredStatus(res);
        if (res?.username) {
          setBirdiesEmail(res.username);
        }
      })
      .catch(err => console.error(err));

    fetchProfileAndStats();
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

      fetchProfileAndStats();
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
      if (res.scrape_status === 'failed') {
        setSaveMessage('Connection failed: check your email/password');
      } else {
        setSaveMessage('Credentials saved successfully!');
      }
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

  const handleSelectAvatar = async (avatarId) => {
    try {
      const res = await api.put('/profile', { avatar_url: avatarId });
      setProfileData(res);
      setShowAvatarSelector(false);
      // Refresh statistics (including leaderboard rankings/avatars)
      fetchProfileAndStats();
    } catch (err) {
      console.error('Failed to update avatar:', err);
    }
  };

  const matchedAvatar = GOLFER_AVATARS.find(a => a.id === profileData?.avatar_url);

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
            <div className="flex-between" style={{ marginBottom: 'var(--space-lg)', justifyContent: 'flex-end' }}>
              <button className="btn-secondary btn-sm">Edit</button>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-lg)' }}>
              <div 
                className="avatar avatar-xl"
                style={{ 
                  cursor: 'pointer', 
                  userSelect: 'none',
                  fontSize: matchedAvatar ? '3.5rem' : 'inherit',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: matchedAvatar ? 'var(--bg-tertiary)' : 'var(--gradient-primary)',
                  border: '2px dashed rgba(16, 185, 129, 0.4)'
                }}
                onClick={() => setShowAvatarSelector(!showAvatarSelector)}
                title="Click to select a cheeky golfer avatar!"
              >
                {matchedAvatar ? (
                  matchedAvatar.emoji
                ) : (
                  user?.display_name
                    ? user.display_name
                        .split(' ')
                        .map((w) => w[0])
                        .join('')
                        .toUpperCase()
                        .slice(0, 2)
                    : '?'
                )}
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

            {/* Avatar Selector Dropdown Grid */}
            {showAvatarSelector && (
              <div 
                className="glass-card" 
                style={{ 
                  marginTop: 'var(--space-md)', 
                  padding: 'var(--space-md)', 
                  background: 'var(--bg-secondary)',
                  border: '1.5px solid var(--accent-emerald)',
                  animation: 'fadeIn 0.2s ease-out'
                }}
              >
                <div className="flex-between" style={{ marginBottom: 'var(--space-sm)' }}>
                  <h4 style={{ fontSize: 'var(--font-sm)', color: 'var(--text-secondary)' }}>Select A Cheeky Golfer Avatar</h4>
                  <button 
                    className="btn-ghost btn-sm" 
                    onClick={() => setShowAvatarSelector(false)}
                    style={{ padding: '2px 8px', fontSize: 'var(--font-xs)' }}
                  >
                    Close ✕
                  </button>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 'var(--space-sm)' }}>
                  {GOLFER_AVATARS.map((avatar) => {
                    const isSelected = profileData?.avatar_url === avatar.id;
                    return (
                      <button
                        key={avatar.id}
                        type="button"
                        onClick={() => handleSelectAvatar(avatar.id)}
                        title={`${avatar.name} (Based on ${avatar.golfer})`}
                        style={{
                          fontSize: '2rem',
                          background: isSelected ? 'rgba(16, 185, 129, 0.15)' : 'var(--bg-tertiary)',
                          border: isSelected ? '2.5px solid var(--accent-emerald)' : '1.5px solid var(--glass-border)',
                          borderRadius: 'var(--radius-md)',
                          padding: '8px',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          transition: 'all 0.15s ease'
                        }}
                        onMouseEnter={() => setHoveredAvatar(avatar)}
                        onMouseLeave={() => setHoveredAvatar(null)}
                      >
                        {avatar.emoji}
                      </button>
                    );
                  })}
                </div>
                <div style={{ minHeight: '20px', marginTop: 'var(--space-sm)', textAlign: 'center', fontSize: 'var(--font-xs)', color: 'var(--text-muted)' }}>
                  {hoveredAvatar ? `${hoveredAvatar.name} — Based on ${hoveredAvatar.golfer}` : 'Hover to see details'}
                </div>
              </div>
            )}

            <div className="divider" />

            <div className="grid-3" style={{ textAlign: 'center' }}>
              <div>
                <div style={{ fontSize: 'var(--font-2xl)', fontWeight: 700, color: 'var(--accent-emerald)' }}>
                  {playerStats.rounds}
                </div>
                <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-muted)', marginTop: 4 }}>
                  Rounds
                </div>
              </div>
              <div>
                <div style={{ fontSize: 'var(--font-2xl)', fontWeight: 700, color: 'var(--accent-gold)' }}>
                  {playerStats.avgScore}
                </div>
                <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-muted)', marginTop: 4 }}>
                  Avg Score
                </div>
              </div>
              <div>
                <div style={{ fontSize: 'var(--font-2xl)', fontWeight: 700 }}>
                  {playerStats.handicap}
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
                credStatus.scrape_status === 'failed' ? (
                  <span className="badge badge-red">Connection Failed</span>
                ) : credStatus.scrape_status === 'pending' ? (
                  <span className="badge badge-gold">Pending</span>
                ) : (
                  <span className="badge badge-emerald">Connected</span>
                )
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
                backgroundColor: saveMessage.includes('successfully') ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                border: `1px solid ${saveMessage.includes('successfully') ? 'var(--accent-emerald)' : 'var(--accent-ruby)'}`,
                fontSize: 'var(--font-sm)', 
                color: saveMessage.includes('successfully') ? 'var(--accent-emerald)' : 'var(--accent-ruby)' 
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
