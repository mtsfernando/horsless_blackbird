import { useParams } from 'react-router-dom';

function PlayerProfile() {
  const { id } = useParams();

  const placeholderStats = [
    { label: 'Rounds', value: '—', color: 'var(--text-primary)' },
    { label: 'Avg Score', value: '—', color: 'var(--accent-emerald)' },
    { label: 'Best Score', value: '—', color: 'var(--accent-gold)' },
    { label: 'Handicap', value: '—', color: 'var(--accent-emerald)' },
  ];

  const placeholderRounds = [
    { date: 'May 18, 2026', course: 'Pebble Beach', score: 78, diff: '+6' },
    { date: 'May 12, 2026', course: 'Augusta National', score: 74, diff: '+2' },
    { date: 'May 5, 2026', course: 'St Andrews', score: 81, diff: '+9' },
  ];

  return (
    <div className="page">
      {/* Player Header */}
      <div
        className="glass-card slide-up"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 'var(--space-xl)',
          marginBottom: 'var(--space-xl)',
        }}
      >
        <div className="avatar avatar-xl">P{id}</div>
        <div>
          <h2 style={{ marginBottom: 'var(--space-xs)' }}>Player #{id}</h2>
          <p className="text-secondary" style={{ fontSize: 'var(--font-sm)' }}>
            Member since 2026
          </p>
          <div style={{ marginTop: 'var(--space-sm)', display: 'flex', gap: 'var(--space-sm)' }}>
            <span className="badge badge-emerald">Active</span>
            <span className="badge badge-gold">Low Handicap</span>
          </div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid-4 stagger-children" style={{ marginBottom: 'var(--space-xl)' }}>
        {placeholderStats.map((stat) => (
          <div className="glass-card stat-card" key={stat.label}>
            <div className="stat-value" style={{ color: stat.color }}>
              {stat.value}
            </div>
            <div className="stat-label">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Round History */}
      <div className="glass-card slide-up" style={{ padding: 0, overflow: 'hidden' }}>
        <div style={{ padding: 'var(--space-lg) var(--space-lg) 0' }}>
          <h3>Round History</h3>
        </div>

        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 'var(--space-md)' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--glass-border)', textAlign: 'left' }}>
              <th style={thStyle}>Date</th>
              <th style={thStyle}>Course</th>
              <th style={thStyle}>Score</th>
              <th style={{ ...thStyle, textAlign: 'right' }}>vs Par</th>
            </tr>
          </thead>
          <tbody>
            {placeholderRounds.map((round, i) => (
              <tr
                key={i}
                style={{
                  borderBottom: '1px solid rgba(16, 185, 129, 0.07)',
                  transition: 'background var(--transition-fast)',
                }}
                onMouseEnter={(e) =>
                  (e.currentTarget.style.background = 'var(--bg-hover)')
                }
                onMouseLeave={(e) =>
                  (e.currentTarget.style.background = 'transparent')
                }
              >
                <td style={tdStyle}>
                  <span style={{ color: 'var(--text-muted)', fontSize: 'var(--font-sm)' }}>
                    {round.date}
                  </span>
                </td>
                <td style={tdStyle}>
                  <span style={{ fontWeight: 600 }}>{round.course}</span>
                </td>
                <td style={tdStyle}>
                  <span
                    style={{
                      fontWeight: 700,
                      fontSize: 'var(--font-lg)',
                      color: 'var(--accent-emerald)',
                    }}
                  >
                    {round.score}
                  </span>
                </td>
                <td style={{ ...tdStyle, textAlign: 'right' }}>
                  <span
                    className="badge badge-neutral"
                    style={{
                      color:
                        parseInt(round.diff) <= 2
                          ? 'var(--accent-emerald-light)'
                          : 'var(--accent-gold-light)',
                      borderColor:
                        parseInt(round.diff) <= 2
                          ? 'rgba(16, 185, 129, 0.25)'
                          : 'rgba(245, 158, 11, 0.25)',
                      background:
                        parseInt(round.diff) <= 2
                          ? 'rgba(16, 185, 129, 0.15)'
                          : 'rgba(245, 158, 11, 0.15)',
                    }}
                  >
                    {round.diff}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Score Trend Placeholder */}
      <div
        className="glass-card glass-card-static"
        style={{
          marginTop: 'var(--space-xl)',
          textAlign: 'center',
          padding: 'var(--space-3xl)',
        }}
      >
        <div style={{ fontSize: '3rem', marginBottom: 'var(--space-md)', opacity: 0.6 }}>📈</div>
        <h3 style={{ marginBottom: 'var(--space-sm)', color: 'var(--text-secondary)' }}>
          Score Trend Chart
        </h3>
        <p className="text-muted" style={{ maxWidth: 400, margin: '0 auto' }}>
          A visual breakdown of scoring trends over time will appear here once data is loaded.
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
};

export default PlayerProfile;
