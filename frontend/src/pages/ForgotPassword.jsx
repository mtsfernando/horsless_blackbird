import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { post } from '../api/client';

function ForgotPassword() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [devToken, setDevToken] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setMessage('');
    setDevToken('');
    setLoading(true);

    try {
      const response = await post('/auth/forgot-password', { email });
      setMessage(response.message || 'If the email exists, a password reset link has been sent.');
      if (response.dev_token) {
        setDevToken(response.dev_token);
      }
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card glass-card">
        <div className="auth-header">
          <div style={{ fontSize: '3rem', marginBottom: 'var(--space-md)' }}>🔑</div>
          <h2>Reset Password</h2>
          <p className="text-secondary">
            Enter your email address and we will provide a recovery token.
          </p>
        </div>

        {error && <div className="auth-error">{error}</div>}
        {message && (
          <div className="auth-error" style={{ background: 'rgba(16, 185, 129, 0.1)', borderColor: 'rgba(16, 185, 129, 0.25)', color: 'var(--accent-emerald-light)' }}>
            {message}
          </div>
        )}

        {!devToken ? (
          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="input-group">
              <label className="input-label" htmlFor="email">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                className="input-field"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoFocus
              />
            </div>

            <button
              type="submit"
              className="btn-primary btn-lg"
              disabled={loading}
              style={{ width: '100%', marginTop: 'var(--space-sm)' }}
            >
              {loading ? (
                <>
                  <span className="spinner" />
                  Sending Request...
                </>
              ) : (
                'Request Reset Token'
              )}
            </button>
          </form>
        ) : (
          <div style={{ marginTop: 'var(--space-md)' }}>
            <div className="input-group" style={{ marginBottom: 'var(--space-md)' }}>
              <label className="input-label">Dev Mode Recovery Token:</label>
              <textarea
                className="input-field"
                readOnly
                rows={4}
                value={devToken}
                style={{ fontFamily: 'monospace', fontSize: 'var(--font-xs)', resize: 'none' }}
              />
            </div>
            <button
              type="button"
              className="btn-primary btn-lg"
              style={{ width: '100%' }}
              onClick={() => navigate(`/reset-password?token=${encodeURIComponent(devToken)}`)}
            >
              Proceed to Reset Password
            </button>
          </div>
        )}

        <div className="auth-footer">
          Remembered your password?{' '}
          <Link to="/login">Sign in</Link>
        </div>
      </div>
    </div>
  );
}

export default ForgotPassword;
