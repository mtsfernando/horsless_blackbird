function Dashboard() {
  const placeholderPlayers = [
    { rank: 1, name: 'Jordan S.', handicap: 4.2, avgScore: 74, trend: '↑' },
    { rank: 2, name: 'Scottie M.', handicap: 5.1, avgScore: 76, trend: '→' },
    { rank: 3, name: 'Rory L.', handicap: 6.8, avgScore: 78, trend: '↓' },
    { rank: 4, name: 'Brooks K.', handicap: 7.3, avgScore: 79, trend: '↑' },
  ];

  return (
    <div className="page">
      <div className="section-header">
        <div className="section-title">
          <span className="section-title-icon">🏆</span>
          <h2>Leaderboard</h2>
        </div>
        <span className="badge badge-emerald">Live</span>
      </div>

      {/* Stats Overview */}
      <div className="grid-4 stagger-children" style={{ marginBottom: 'var(--space-xl)' }}>
        <div className="glass-card stat-card">
          <div className="stat-value stat-value-emerald">12</div>
          <div className="stat-label">Active Players</div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-value stat-value-gold">74.2</div>
          <div className="stat-label">Avg Score</div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-value">48</div>
          <div className="stat-label">Rounds Played</div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-value stat-value-emerald">5.4</div>
          <div className="stat-label">Avg Handicap</div>
        </div>
      </div>

      {/* Leaderboard Table */}
      <div className="glass-card slide-up" style={{ padding: 0, overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr
              style={{
                borderBottom: '1px solid var(--glass-border)',
                textAlign: 'left',
              }}
            >
              <th style={thStyle}>#</th>
              <th style={thStyle}>Player</th>
              <th style={thStyle}>Handicap</th>
              <th style={thStyle}>Avg Score</th>
              <th style={{ ...thStyle, textAlign: 'center' }}>Trend</th>
            </tr>
          </thead>
          <tbody>
            {placeholderPlayers.map((player) => (
              <tr
                key={player.rank}
                style={{
                  borderBottom: '1px solid rgba(16, 185, 129, 0.07)',
                  transition: 'background var(--transition-fast)',
                  cursor: 'pointer',
                }}
                onMouseEnter={(e) =>
                  (e.currentTarget.style.background = 'var(--bg-hover)')
                }
                onMouseLeave={(e) =>
                  (e.currentTarget.style.background = 'transparent')
                }
              >
                <td style={tdStyle}>
                  <span
                    style={{
                      fontWeight: 700,
                      color:
                        player.rank === 1
                          ? 'var(--accent-gold)'
                          : player.rank === 2
                          ? 'var(--text-secondary)'
                          : player.rank === 3
                          ? '#CD7F32'
                          : 'var(--text-muted)',
                    }}
                  >
                    {player.rank}
                  </span>
                </td>
                <td style={tdStyle}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                    <div className="avatar" style={{ width: 32, height: 32, fontSize: 'var(--font-xs)' }}>
                      {player.name
                        .split(' ')
                        .map((w) => w[0])
                        .join('')}
                    </div>
                    <span style={{ fontWeight: 600 }}>{player.name}</span>
                  </div>
                </td>
                <td style={tdStyle}>
                  <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>
                    {player.handicap}
                  </span>
                </td>
                <td style={tdStyle}>{player.avgScore}</td>
                <td style={{ ...tdStyle, textAlign: 'center', fontSize: 'var(--font-lg)' }}>
                  <span
                    style={{
                      color:
                        player.trend === '↑'
                          ? 'var(--accent-emerald)'
                          : player.trend === '↓'
                          ? 'var(--accent-red)'
                          : 'var(--text-muted)',
                    }}
                  >
                    {player.trend}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Coming Soon */}
      <div
        className="glass-card glass-card-static"
        style={{
          marginTop: 'var(--space-xl)',
          textAlign: 'center',
          padding: 'var(--space-3xl)',
        }}
      >
        <div style={{ fontSize: '3rem', marginBottom: 'var(--space-md)', opacity: 0.6 }}>📊</div>
        <h3 style={{ marginBottom: 'var(--space-sm)', color: 'var(--text-secondary)' }}>
          More Stats Coming Soon
        </h3>
        <p className="text-muted" style={{ maxWidth: 400, margin: '0 auto' }}>
          Detailed analytics, round-by-round breakdowns, and head-to-head comparisons are on the way.
        </p>
      </div>
    </div>
  );
}

const thStyle = {
  padding: '14px 20px',
  fontSize: 'var(--font-xs)',
  fontWeight: 600,
  color: 'var(--text-muted)',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
};

const tdStyle = {
  padding: '14px 20px',
  fontSize: 'var(--font-sm)',
};

export default Dashboard;
