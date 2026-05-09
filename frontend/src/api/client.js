/* ═══════════════════════════════════════════════════════════════════════════
   api/client.js — API Client
   ═══════════════════════════════════════════════════════════════════════════
   Two functions:
   1. fetchRecommendation — POSTs UserInput to /recommend
   2. fetchScoreInsights  — POSTs the full response to /explain-scores
      to get OpenAI-powered per-score reasoning
   ═══════════════════════════════════════════════════════════════════════════ */
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
/**
 * Send a UserInput payload to the backend and return the RecommendationResponse.
 *
 * @param {object} userInput — matches the backend's UserInput schema
 * @returns {Promise<object>} — RecommendationResponse from FastAPI
 */
export async function fetchRecommendation(userInput) {
  const response = await fetch(`${API_URL}/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(userInput),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API Error ${response.status}: ${errorBody}`);
  }

  return response.json();
}

/**
 * Send the full recommendation response to the backend for OpenAI-powered
 * per-score insights. Returns { available: boolean, insights: {...} }.
 *
 * @param {object} recommendationResponse — the full backend response
 * @returns {Promise<{available: boolean, insights: object}>}
 */
export async function fetchScoreInsights(recommendationResponse) {
  try {
    const response = await fetch(`${API_URL}/explain-scores`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(recommendationResponse),
    });

    if (!response.ok) return { available: false, insights: {} };

    return response.json();
  } catch {
    return { available: false, insights: {} };
  }
}
