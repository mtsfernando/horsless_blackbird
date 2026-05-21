import { useState } from 'react';
import { useApi } from '../hooks/useApi';

function Activity() {
  const { data: activities, loading, error } = useApi('/activity');
  const [expandedRounds, setExpandedRounds] = useState({});

  const toggleRound = (id) => {
    setExpandedRounds((prev) => ({
      ...prev,
      [id]: !prev[id],
    }));
  };

  const formatDate = (dateStr) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const getRelativeTime = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffMins < 60) {
      return diffMins <= 1 ? 'just now' : `${diffMins}m ago`;
    } else if (diffHours < 24) {
      return `${diffHours}h ago`;
    } else if (diffDays < 7) {
      return `${diffDays}d ago`;
    }
    return formatDate(dateStr);
  };

  return (
    <div className="page" style={{ maxWidth: '800px', margin: '0 auto', padding: 'var(--space-xl) var(--space-md)' }}>
      {/* Local Page Custom Styles */}
      <style>{`
        .timeline {
          position: relative;
          padding-left: 2rem;
          border-left: 2px dashed rgba(16, 185, 129, 0.15);
          margin-left: 1rem;
          margin-top: var(--space-xl);
        }
        .timeline-item {
          position: relative;
          margin-bottom: var(--space-xl);
          animation: slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
        }
        .timeline-dot {
          position: absolute;
          left: calc(-2rem - 7px);
          top: 24px;
          width: 12px;
          height: 12px;
          border-radius: 50%;
          background: var(--accent-emerald);
          box-shadow: 0 0 8px var(--accent-emerald);
          border: 2px solid var(--bg-primary);
        }
        .timeline-dot.social {
          background: var(--accent-gold);
          box-shadow: 0 0 8px var(--accent-gold);
        }
        .card-header-flex {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: var(--space-md);
        }
        .scorecard-mini-grid {
          display: flex;
          gap: var(--space-md);
          margin-bottom: var(--space-sm);
        }
        .scorecard-mini-item {
          flex: 1;
          background: rgba(255, 255, 255, 0.02);
          border-radius: var(--radius-md);
          padding: var(--space-sm) var(--space-md);
          text-align: center;
          border: 1px solid rgba(16, 185, 129, 0.05);
        }
        .scorecard-mini-value {
          font-size: var(--font-lg);
          font-weight: 700;
          color: var(--text-primary);
        }
        .scorecard-mini-label {
          font-size: var(--font-xs);
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.05em;
          margin-top: 2px;
        }
        .expand-button {
          background: transparent;
          color: var(--accent-emerald-light);
          font-weight: 600;
          font-size: var(--font-sm);
          display: flex;
          align-items: center;
          gap: 6px;
          transition: color var(--transition-fast);
          margin-top: var(--space-sm);
          padding: var(--space-xs) var(--space-sm);
          border-radius: var(--radius-sm);
        }
        .expand-button:hover {
          color: var(--accent-emerald);
          background: var(--bg-hover);
        }
        .scorecard-expanded-table-container {
          overflow-x: auto;
          margin-top: var(--space-md);
          background: rgba(0, 0, 0, 0.2);
          border-radius: var(--radius-md);
          padding: var(--space-md);
          border: 1px solid rgba(16, 185, 129, 0.08);
          animation: slideDown 0.25s cubic-bezier(0.16, 1, 0.3, 1) both;
        }
        .scorecard-expanded-table {
          width: 100%;
          border-collapse: collapse;
          text-align: center;
        }
        .scorecard-expanded-table th, .scorecard-expanded-table td {
          padding: 8px 6px;
          font-size: var(--font-xs);
          border-bottom: 1px solid rgba(255, 255, 255, 0.04);
        }
        .scorecard-expanded-table th {
          color: var(--text-muted);
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.02em;
        }
        .score-circle {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 24px;
          height: 24px;
          border-radius: 50%;
          font-weight: 700;
          font-size: 11px;
        }
        .score-birdie {
          background: rgba(245, 158, 11, 0.12);
          color: var(--accent-gold-light);
          border: 1px solid var(--accent-gold);
          box-shadow: 0 0 6px rgba(245, 158, 11, 0.15);
        }
        .score-par {
          background: rgba(16, 185, 129, 0.12);
          color: var(--accent-emerald-light);
          border: 1px solid var(--accent-emerald);
        }
        .score-bogey {
          background: rgba(239, 68, 68, 0.12);
          color: #FCA5A5;
          border: 1px solid var(--accent-red);
        }
        .score-double-bogey {
          background: rgba(185, 28, 28, 0.2);
          color: #FECACA;
          border: 1px solid #EF4444;
        }
      `}</style>

      <div className="section-header">
        <div className="section-title">
          <span className="section-title-icon">⛳</span>
          <h2>Activity Timeline</h2>
        </div>
        <span className="badge badge-emerald">Updates</span>
      </div>

      {loading ? (
        <div style={{ padding: 'var(--space-3xl) 0', textAlign: 'center', color: 'var(--text-secondary)' }}>
          <span className="spinner" style={{ marginRight: 8 }} /> Loading activities...
        </div>
      ) : error ? (
        <div style={{ padding: 'var(--space-3xl) 0', textAlign: 'center', color: 'var(--accent-red)' }}>
          ⚠️ Error loading activities: {error}
        </div>
      ) : !activities || activities.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: 'var(--space-3xl)' }}>
          <div style={{ fontSize: '3rem', marginBottom: 'var(--space-md)', opacity: 0.6 }}>🏌️‍♂️</div>
          <h3 style={{ marginBottom: 'var(--space-sm)', color: 'var(--text-secondary)' }}>No Activity Recorded</h3>
          <p className="text-muted" style={{ maxWidth: 450, margin: '0 auto' }}>
            Rounds and social connections imported from 18Birdies will appear on this unified feed. Go to your Profile to sync your data.
          </p>
        </div>
      ) : (
        <div className="timeline">
          {activities.map((item) => {
            const isRound = item.type === 'round';
            const relativeTime = getRelativeTime(item.date);
            const isExpanded = !!expandedRounds[item.id];

            if (isRound) {
              return (
                <div key={item.id} className="timeline-item">
                  <div className="timeline-dot" />
                  <div className="glass-card glass-card-interactive">
                    <div className="card-header-flex">
                      <div>
                        <span className="badge badge-neutral" style={{ marginBottom: 'var(--space-xs)' }}>
                          🏌️‍♂️ Golf Round
                        </span>
                        <h4 style={{ margin: '4px 0 2px' }}>{item.course}</h4>
                        <span style={{ fontSize: 'var(--font-xs)', color: 'var(--text-muted)' }}>
                          Played {formatDate(item.date)}
                        </span>
                      </div>
                      <span
                        className="badge badge-emerald"
                        style={{ fontSize: 'var(--font-xs)', letterSpacing: '0.02em' }}
                      >
                        {item.holes} Holes
                      </span>
                    </div>

                    <div className="scorecard-mini-grid">
                      <div className="scorecard-mini-item">
                        <div className="scorecard-mini-value" style={{ color: 'var(--accent-gold-light)' }}>
                          {item.score}
                        </div>
                        <div className="scorecard-mini-label">Strokes</div>
                      </div>
                      <div className="scorecard-mini-item">
                        <div className="scorecard-mini-value">
                          {item.putts ?? '--'}
                        </div>
                        <div className="scorecard-mini-label">Putts</div>
                      </div>
                      <div className="scorecard-mini-item">
                        <div className="scorecard-mini-value" style={{ color: 'var(--accent-emerald-light)' }}>
                          {item.scorecard ? Math.round((item.scorecard.reduce((a,b)=>a+b, 0) / item.holes)) : '--'}
                        </div>
                        <div className="scorecard-mini-label">Avg Stroke</div>
                      </div>
                    </div>

                    <button className="expand-button" onClick={() => toggleRound(item.id)}>
                      {isExpanded ? '▲ Collapse Details' : '▼ Expand Scorecard'}
                    </button>

                    {isExpanded && item.scorecard && item.pars && (
                      <div className="scorecard-expanded-table-container">
                        <table className="scorecard-expanded-table">
                          <thead>
                            <tr>
                              <th style={{ textAlign: 'left' }}>Hole</th>
                              {item.scorecard.map((_, idx) => (
                                <th key={idx}>{idx + 1}</th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            <tr>
                              <td style={{ textAlign: 'left', fontWeight: 600, color: 'var(--text-muted)' }}>Par</td>
                              {item.pars.map((par, idx) => (
                                <td key={idx} style={{ fontWeight: 600 }}>{par}</td>
                              ))}
                            </tr>
                            <tr>
                              <td style={{ textAlign: 'left', fontWeight: 600, color: 'var(--text-primary)' }}>Score</td>
                              {item.scorecard.map((score, idx) => {
                                const par = item.pars[idx];
                                const diff = score - par;
                                let scoreClass = 'score-par';
                                if (diff <= -1) scoreClass = 'score-birdie';
                                else if (diff === 0) scoreClass = 'score-par';
                                else if (diff === 1) scoreClass = 'score-bogey';
                                else if (diff >= 2) scoreClass = 'score-double-bogey';

                                return (
                                  <td key={idx}>
                                    <span className={`score-circle ${scoreClass}`}>{score}</span>
                                  </td>
                                );
                              })}
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    )}

                    <div style={{ marginTop: 'var(--space-md)', textAlign: 'right' }}>
                      <span style={{ fontSize: 'var(--font-xs)', color: 'var(--text-muted)' }}>
                        Synced {relativeTime}
                      </span>
                    </div>
                  </div>
                </div>
              );
            } else {
              // Social announcement
              return (
                <div key={item.id} className="timeline-item">
                  <div className="timeline-dot social" />
                  <div className="glass-card glass-card-interactive" style={{ borderLeft: '3px solid var(--accent-gold)' }}>
                    <div className="card-header-flex" style={{ marginBottom: 'var(--space-xs)' }}>
                      <span className="badge badge-gold">
                        🤝 Social Link
                      </span>
                      <span style={{ fontSize: 'var(--font-xs)', color: 'var(--text-muted)' }}>
                        {relativeTime}
                      </span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-md)', padding: 'var(--space-sm) 0' }}>
                      <div style={{ fontSize: '1.8rem' }}>👥</div>
                      <div>
                        <p style={{ color: 'var(--text-primary)', fontWeight: 500, margin: 0 }}>
                          {item.content}
                        </p>
                        <span style={{ fontSize: 'var(--font-xs)', color: 'var(--text-muted)' }}>
                          Connected on {formatDate(item.date)}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            }
          })}
        </div>
      )}
    </div>
  );
}

export default Activity;
