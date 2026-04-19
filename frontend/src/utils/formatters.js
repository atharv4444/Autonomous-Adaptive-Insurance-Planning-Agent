/**
 * Format a number as Indian Rupees.
 */
export function formatCurrency(value) {
  if (value === undefined || value === null) return '₹0';
  return '₹' + Number(value).toLocaleString('en-IN', { maximumFractionDigits: 0 });
}

/**
 * Format as percentage.
 */
export function formatPercent(value, decimals = 1) {
  if (value === undefined || value === null) return '0%';
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Format a number with commas.
 */
export function formatNumber(value, decimals = 1) {
  if (value === undefined || value === null) return '0';
  return Number(value).toFixed(decimals);
}

/**
 * Format duration in ms.
 */
export function formatDuration(ms) {
  if (ms < 1000) return `${ms.toFixed(1)}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}
