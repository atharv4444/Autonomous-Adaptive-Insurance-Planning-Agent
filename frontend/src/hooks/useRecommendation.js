import { useState, useCallback } from 'react';
import { fetchRecommendation } from '../api/client';

/**
 * Custom hook for managing recommendation state and API calls.
 */
export function useRecommendation() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [userPayload, setUserPayload] = useState(null);

  const submitRecommendation = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchRecommendation(payload);
      setResult(data);
      setUserPayload(payload);
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
    setUserPayload(null);
  }, []);

  return {
    result,
    loading,
    error,
    userPayload,
    submitRecommendation,
    reset,
  };
}
