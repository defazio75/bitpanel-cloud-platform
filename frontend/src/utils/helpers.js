// src/utils/helpers.js

// Format a date as MM/DD/YYYY
export function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US');
}

// Format a number with 2 decimals
export function formatNumber(num, decimals = 2) {
  return Number(num).toFixed(decimals);
}

// Capitalize first letter of a string
export function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}
