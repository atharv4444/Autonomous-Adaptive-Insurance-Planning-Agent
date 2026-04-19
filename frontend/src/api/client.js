const API_BASE = '/api';

/**
 * Call the backend recommendation endpoint.
 * @param {object} payload — UserInput fields matching the backend schema
 * @returns {Promise<object>} — RecommendationResponse
 */
export async function fetchRecommendation(payload) {
  const response = await fetch(`${API_BASE}/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API error ${response.status}`);
  }

  return response.json();
}

/**
 * Simple health check.
 */
export async function healthCheck() {
  const response = await fetch(`${API_BASE}/health`);
  return response.json();
}
