import { useState, useEffect, useCallback } from 'react';
import { get } from '../api/client';

export function useApi(path, options = {}) {
  const { immediate = true } = options;
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(immediate);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const result = await get(path);
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [path]);

  useEffect(() => {
    if (immediate) {
      fetchData();
    }
  }, [immediate, fetchData]);

  return { data, error, loading, refetch: fetchData };
}

export default useApi;
