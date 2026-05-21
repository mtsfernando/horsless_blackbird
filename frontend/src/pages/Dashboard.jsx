import { useApi } from '../hooks/useApi';

function Dashboard() {
  const { data: leaderboard, loading: leadLoading, error: leadError } = useApi('/leaderboard');
  const { data: stats, loading: statsLoading } = useApi('/leaderboard/stats');

  const activePlayers = stats?.total_players ?? 0;
  const avgScore = stats?.overall_avg_score ? stats.overall_avg_score.toFixed(1) : '--';
  const totalRounds = stats?.total_rounds ?? 0;
  // Calculate average handicap across all players with scores
  const avgHandicap = stats?.overall_avg_score ? ((stats.overall_avg_score - 72) * 0.96).toFixed(1) : '--';

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
          <div className="stat-value stat-value-emerald">
            {statsLoading ? '...' : activePlayers}
          </div>
          <div className="stat-label">Active Players</div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-value stat-value-gold">
            {statsLoading ? '...' : avgScore}
          </div>
          <div className="stat-label">Avg Score</div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-value">
            {statsLoading ? '...' : totalRounds}
          </div>
          <div className="stat-label">Rounds Played</div>
        </div>
        <div className="glass-card stat-card">
          <div className="stat-value stat-value-emerald">
            {statsLoading ? '...' : avgHandicap}
          </div>
          <div className="stat-label">Avg Handicap</div>
        </div>
      </div>

      {/* Leaderboard Table */}
      <div className="glass-card slide-up" style={{ padding: 0, overflow: 'hidden' }}>
        {leadLoading ? (
          <div style={{ padding: 'var(--space-2xl)', textAlign: 'center', color: 'var(--text-muted)' }}>
            <span className="spinner" style={{ marginRight: 8 }} /> Loading leaderboard...
          </div>
        ) : leadError ? (
          <div style={{ padding: 'var(--space-2xl)', textAlign: 'center', color: 'var(--accent-red)' }}>
            Error loading leaderboard: {leadError}
          </div>
        ) : !leaderboard || leaderboard.length === 0 ? (
          <div style={{ padding: 'var(--space-2xl)', textAlign: 'center', color: 'var(--text-muted)' }}>
            No players registered on the platform yet.
          </div>
        ) : (
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
                <th style={thStyle}>Rounds</th>
                <th style={thStyle}>Handicap</th>
                <th style={thStyle}>Avg Score</th>
                <th style={thStyle}>Best Score</th>
              </tr>
            </thead>
            <tbody>
              {leaderboard.map((player, index) => {
                const rank = index + 1;
                const handicapVal = player.avg_score ? ((player.avg_score - 72) * 0.96).toFixed(1) : '--';
                const avgScoreVal = player.avg_score ? Math.round(player.avg_score) : '--';
                const bestScoreVal = player.best_score ?? '--';

                return (
                  <tr
                    key={player.player_id}
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
                            rank === 1
                              ? 'var(--accent-gold)'
                              : rank === 2
                              ? 'var(--text-secondary)'
                              : rank === 3
                              ? '#CD7F32'
                              : 'var(--text-muted)',
                        }}
                      >
                        {rank}
                      </span>
                    </td>
                    <td style={tdStyle}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-sm)' }}>
                        <div className="avatar" style={{ width: 32, height: 32, fontSize: 'var(--font-xs)' }}>
                          {player.display_name
                            ? player.display_name
                                .split(' ')
                                .map((w) => w[0])
                                .join('')
                                .toUpperCase()
                                .slice(0, 2)
                            : '?'}
                        </div>
                        <span style={{ fontWeight: 600 }}>{player.display_name || 'Golfer'}</span>
                      </div>
                    </td>
                    <td style={tdStyle}>{player.rounds_played}</td>
                    <td style={tdStyle}>
                      <span style={{ color: 'var(--accent-emerald)', fontWeight: 600 }}>
                        {handicapVal}
                      </span>
                    </td>
                    <td style={tdStyle}>{avgScoreVal}</td>
                    <td style={tdStyle}>{bestScoreVal}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
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

      {/* Brand Footer */}
      <div style={{ textAlign: 'center', padding: 'var(--space-2xl) 0 var(--space-xl)', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--space-sm)' }}>
        <img src="/logo.png" alt="Horseless Blackbird" style={{ width: 36, height: 36, objectFit: 'contain', opacity: 0.4 }} />
        <span style={{ fontSize: 'var(--font-xs)', color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
          Horseless Blackbird · Golf Tracker
        </span>
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
