import { useState, useRef, useEffect } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();
  
  // Theme toggle state and effect
  const [theme, setTheme] = useState(localStorage.getItem('blackbird-theme') || 'dark');

  useEffect(() => {
    if (theme === 'light') {
      document.documentElement.setAttribute('data-theme', 'light');
    } else {
      document.documentElement.removeAttribute('data-theme');
    }
  }, [theme]);

  function toggleTheme() {
    const nextTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(nextTheme);
    localStorage.setItem('blackbird-theme', nextTheme);
  }

  useEffect(() => {
    function handleClickOutside(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  function handleLogout() {
    logout();
    setDropdownOpen(false);
    navigate('/login');
  }

  function getInitials(name) {
    if (!name) return '?';
    return name
      .split(' ')
      .map((w) => w[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  }

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          <span>Horseless Blackbird</span>
        </Link>

        {isAuthenticated && (
          <ul className="navbar-links">
            <li>
              <NavLink
                to="/"
                end
                className={({ isActive }) =>
                  `navbar-link${isActive ? ' active' : ''}`
                }
              >
                Dashboard
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/activity"
                className={({ isActive }) =>
                  `navbar-link${isActive ? ' active' : ''}`
                }
              >
                Activity
              </NavLink>
            </li>
            <li>
              <NavLink
                to="/profile"
                className={({ isActive }) =>
                  `navbar-link${isActive ? ' active' : ''}`
                }
              >
                Profile
              </NavLink>
            </li>
          </ul>
        )}

        <div className="navbar-actions">
          <button
            className="theme-toggle-btn"
            onClick={toggleTheme}
            aria-label="Toggle theme"
            style={{
              background: 'transparent',
              border: '1px solid var(--glass-border)',
              color: 'var(--text-primary)',
              fontSize: '1.1rem',
              padding: '6px 10px',
              borderRadius: 'var(--radius-sm)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '8px',
              transition: 'all var(--transition-fast)'
            }}
          >
            🌓
          </button>

          {isAuthenticated ? (
            <div className="dropdown" ref={dropdownRef}>
              <button
                className="avatar"
                onClick={() => setDropdownOpen((prev) => !prev)}
                aria-label="User menu"
                aria-expanded={dropdownOpen}
              >
                {getInitials(user?.display_name || user?.email)}
              </button>
              {dropdownOpen && (
                <div className="dropdown-menu slide-down">
                  <div style={{ padding: '8px 14px', borderBottom: '1px solid var(--glass-border)', marginBottom: '4px' }}>
                    <div style={{ fontSize: 'var(--font-sm)', fontWeight: 600, color: 'var(--text-primary)' }}>
                      {user?.display_name || 'Golfer'}
                    </div>
                    <div style={{ fontSize: 'var(--font-xs)', color: 'var(--text-muted)' }}>
                      {user?.email}
                    </div>
                  </div>

                  <div className="mobile-nav-links">
                    <NavLink to="/" end className="dropdown-item" onClick={() => setDropdownOpen(false)}>
                      📊 Dashboard
                    </NavLink>
                    <NavLink to="/activity" className="dropdown-item" onClick={() => setDropdownOpen(false)}>
                      🏌️ Activity
                    </NavLink>
                    <NavLink to="/profile" className="dropdown-item" onClick={() => setDropdownOpen(false)}>
                      👤 Profile
                    </NavLink>
                  </div>

                  <div className="dropdown-divider" />
                  <button className="dropdown-item" onClick={handleLogout}>
                    🚪 Logout
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link to="/login" className="btn-primary btn-sm">
              Sign In
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
