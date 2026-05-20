import { useAuth } from '../hooks/useAuth';
import { useScrapeProgress } from '../hooks/useScrapeProgress';

function Profile() {
  const { user } = useAuth();
  const { progress, stage, message, isActive, error, startScrape } = useScrapeProgress();

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
              <span className="badge badge-neutral">Not Connected</span>
            </div>

            <p className="text-secondary" style={{ fontSize: 'var(--font-sm)', marginBottom: 'var(--space-lg)' }}>
              Link your 18Birdies account to automatically import your rounds and stats.
            </p>

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
                  disabled
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
                  placeholder="••••••••"
                  disabled
                />
              </div>
              <button className="btn-secondary" disabled>
                Save Credentials
              </button>
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
          </div>

          {/* Recent Activity Placeholder */}
          <div className="glass-card">
            <h3 style={{ marginBottom: 'var(--space-lg)' }}>Recent Activity</h3>

            <div className="empty-state" style={{ padding: 'var(--space-xl)' }}>
              <div className="empty-state-icon">🏌️‍♂️</div>
              <h3 style={{ fontSize: 'var(--font-base)' }}>No activity yet</h3>
              <p style={{ fontSize: 'var(--font-sm)' }}>
                Connect your account and refresh to see your latest rounds here.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Profile;
