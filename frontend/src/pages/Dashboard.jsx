import { useState } from 'react';
import { useApi } from '../hooks/useApi';

function Dashboard() {
  const { data: leaderboard, loading: leadLoading, error: leadError } = useApi('/leaderboard');
  const { data: stats, loading: statsLoading } = useApi('/leaderboard/stats');
  const [selectedPlayerId, setSelectedPlayerId] = useState(null);

  const selectedPlayer = leaderboard?.find(p => p.player_id === selectedPlayerId);

  const activePlayers = stats?.total_players ?? 0;
  const avgScore = stats?.overall_avg_score ? stats.overall_avg_score.toFixed(1) : '--';
  const totalRounds = stats?.total_rounds ?? 0;
  // Calculate average handicap across all players with scores
  const avgHandicap = stats?.overall_avg_score ? ((stats.overall_avg_score - 72) * 0.96).toFixed(1) : '--';

  const handlePlayerClick = (playerId) => {
    if (selectedPlayerId === playerId) {
      setSelectedPlayerId(null);
    } else {
      setSelectedPlayerId(playerId);
    }
  };

  return (
    <div className="page">
      <div className="section-header">
        <div className="section-title">
          <span className="section-title-icon">🏆</span>
          <h2>Leaderboard</h2>
        </div>
        <span className="badge badge-emerald">Live</span>
      </div>

      {/* Selected Player Banner */}
      {selectedPlayer && (
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'rgba(16, 185, 129, 0.08)',
          border: '1px solid rgba(16, 185, 129, 0.2)',
          borderRadius: 'var(--radius-md)',
          padding: 'var(--space-sm) var(--space-md)',
          marginBottom: 'var(--space-lg)',
          fontSize: 'var(--font-sm)',
          animation: 'fadeIn 0.25s ease-out'
        }}>
          <span style={{ color: 'var(--accent-emerald-light)' }}>
            Viewing stats for <strong>{selectedPlayer.display_name}</strong>
          </span>
          <button 
            onClick={() => setSelectedPlayerId(null)}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--accent-emerald-light)',
              cursor: 'pointer',
              fontSize: 'var(--font-xs)',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            Reset to Overall ✕
          </button>
        </div>
      )}

      {/* Stats Overview */}
      <div className="grid-3 stagger-children" style={{ marginBottom: 'var(--space-xl)' }}>
        <div className="glass-card stat-card" style={{ border: selectedPlayer ? '1px solid var(--accent-gold)' : '1px solid var(--glass-border)', transition: 'border 0.3s ease' }}>
          <div className="stat-value stat-value-gold">
            {statsLoading ? '...' : (selectedPlayer ? (selectedPlayer.avg_score ? selectedPlayer.avg_score.toFixed(1) : '--') : avgScore)}
          </div>
          <div className="stat-label">
            {selectedPlayer ? `${selectedPlayer.display_name.split(' ')[0]}'s Avg Score` : 'Avg Score'}
          </div>
        </div>
        <div className="glass-card stat-card" style={{ border: selectedPlayer ? '1px solid var(--accent-emerald)' : '1px solid var(--glass-border)', transition: 'border 0.3s ease' }}>
          <div className="stat-value">
            {statsLoading ? '...' : (selectedPlayer ? selectedPlayer.rounds_played : totalRounds)}
          </div>
          <div className="stat-label">
            {selectedPlayer ? `${selectedPlayer.display_name.split(' ')[0]}'s Rounds` : 'Rounds Played'}
          </div>
        </div>
        <div className="glass-card stat-card" style={{ border: selectedPlayer ? '1px solid var(--accent-emerald)' : '1px solid var(--glass-border)', transition: 'border 0.3s ease' }}>
          <div className="stat-value stat-value-emerald">
            {statsLoading ? '...' : (selectedPlayer ? (selectedPlayer.avg_score ? ((selectedPlayer.avg_score - 72) * 0.96).toFixed(1) : '--') : avgHandicap)}
          </div>
          <div className="stat-label">
            {selectedPlayer ? `${selectedPlayer.display_name.split(' ')[0]}'s Handicap` : 'Avg Handicap'}
          </div>
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
                const isSelected = selectedPlayerId === player.player_id;

                return (
                  <tr
                    key={player.player_id}
                    onClick={() => handlePlayerClick(player.player_id)}
                    style={{
                      borderBottom: '1px solid rgba(16, 185, 129, 0.07)',
                      transition: 'background var(--transition-fast)',
                      cursor: 'pointer',
                      background: isSelected ? 'rgba(16, 185, 129, 0.08)' : 'transparent',
                    }}
                    onMouseEnter={(e) => {
                      if (!isSelected) e.currentTarget.style.background = 'var(--bg-hover)';
                    }}
                    onMouseLeave={(e) => {
                      if (!isSelected) e.currentTarget.style.background = 'transparent';
                    }}
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
                        <div 
                          className="avatar" 
                          style={{ 
                            width: 32, 
                            height: 32, 
                            fontSize: 'var(--font-xs)',
                            border: isSelected ? '2px solid var(--accent-emerald)' : 'none',
                            boxShadow: isSelected ? '0 0 8px rgba(16, 185, 129, 0.4)' : 'none',
                            transition: 'border 0.2s ease, box-shadow 0.2s ease'
                          }}
                        >
                          {player.display_name
                            ? player.display_name
                                .split(' ')
                                .map((w) => w[0])
                                .join('')
                                .toUpperCase()
                                .slice(0, 2)
                            : '?'}
                        </div>
                        <span 
                          style={{ 
                            fontWeight: isSelected ? 800 : 600,
                            color: isSelected ? 'var(--accent-emerald-light)' : 'var(--text-primary)',
                            transition: 'color 0.2s ease, font-weight 0.2s ease'
                          }}
                        >
                          {player.display_name || 'Golfer'}
                        </span>
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
