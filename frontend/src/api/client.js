const BASE_URL = import.meta.env.VITE_API_URL || '/api';

async function request(method, path, body = null) {
  const headers = {
    'Content-Type': 'application/json',
  };

  const token = localStorage.getItem('token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const config = {
    method,
    headers,
  };

  if (body) {
    config.body = JSON.stringify(body);
  }

  const response = await fetch(`${BASE_URL}${path}`, config);

  if (response.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || error.message || `Request failed (${response.status})`);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

export function get(path) {
  return request('GET', path);
}

export function post(path, body) {
  return request('POST', path, body);
}

export function put(path, body) {
  return request('PUT', path, body);
}

export function del(path) {
  return request('DELETE', path);
}

export default { get, post, put, del };
