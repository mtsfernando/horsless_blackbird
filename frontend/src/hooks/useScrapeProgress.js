import { useState, useCallback, useRef, useEffect } from 'react';

const BASE_URL = import.meta.env.VITE_API_URL || '/api';

export function useScrapeProgress() {
  const [progress, setProgress] = useState(0);
  const [stage, setStage] = useState('');
  const [message, setMessage] = useState('');
  const [isActive, setIsActive] = useState(false);
  const [error, setError] = useState(null);

  const eventSourceRef = useRef(null);

  const cleanup = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
  }, []);

  const reset = useCallback(() => {
    cleanup();
    setProgress(0);
    setStage('');
    setMessage('');
    setIsActive(false);
    setError(null);
  }, [cleanup]);

  const startScrape = useCallback(() => {
    cleanup();
    setIsActive(true);
    setError(null);
    setProgress(0);
    setStage('Initializing');
    setMessage('Starting data refresh...');

    const token = localStorage.getItem('token');
    const url = `${BASE_URL}/profile/refresh?token=${encodeURIComponent(token)}`;
    const es = new EventSource(url);
    eventSourceRef.current = es;

    es.addEventListener('scrape_progress', (event) => {
      try {
        const data = JSON.parse(event.data);
        setProgress(data.progress ?? 0);
        setStage(data.stage ?? '');
        setMessage(data.message ?? '');

        if (data.progress >= 100 || data.stage === 'complete') {
          cleanup(); // Close connection immediately
          setTimeout(() => {
            setIsActive(false);
          }, 3000); // Keep progress bar visible for 3 seconds so the user can read the final message
        }
      } catch {
        // ignore parse errors
      }
    });

    es.onerror = () => {
      setError('Connection lost. Please try again.');
      setIsActive(false);
      cleanup();
    };
  }, [cleanup]);

  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  return { progress, stage, message, isActive, error, startScrape, reset };
}

export default useScrapeProgress;
