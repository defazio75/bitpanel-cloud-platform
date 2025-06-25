// frontend/src/utils/api.js

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

async function fetchJSON(url, options = {}) {
  const res = await fetch(url, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API request failed: ${res.status} ${res.statusText} – ${text}`);
  }
  return res.json();
}

// — Prices —
export async function getPrices({ userId, token, mode }) {
  const url = new URL(`${API_BASE_URL}/prices`);
  url.searchParams.set('user_id', userId);
  url.searchParams.set('mode', mode);
  const opts = token 
    ? { headers: { Authorization: `Bearer ${token}` } } 
    : {};
  return fetchJSON(url.toString(), opts);
}

// — Portfolio Snapshot —
export async function getPortfolioSnapshot({ userId, token, mode }) {
  const url = new URL(`${API_BASE_URL}/portfolio`);
  url.searchParams.set('user_id', userId);
  url.searchParams.set('mode', mode);
  const opts = token
    ? { headers: { Authorization: `Bearer ${token}` } }
    : {};
  return fetchJSON(url.toString(), opts);
}

// — Manual Trade —
export async function executeManualTrade({ userId, token, mode, tradeData }) {
  const url = new URL(`${API_BASE_URL}/manual_trade`);
  url.searchParams.set('user_id', userId);
  url.searchParams.set('mode', mode);
  return fetchJSON(url.toString(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    },
    body: JSON.stringify(tradeData),
  });
}

// — Paper Reset —
export async function resetPaperAccount({ userId, token, mode }) {
  const url = new URL(`${API_BASE_URL}/reset_paper`);
  url.searchParams.set('user_id', userId);
  url.searchParams.set('mode', mode);
  return fetchJSON(url.toString(), { method: 'POST' });
}

// — Strategies —
export async function getStrategies({ userId, token, mode }) {
  const url = new URL(`${API_BASE_URL}/strategies`);
  url.searchParams.set('user_id', userId);
  url.searchParams.set('mode', mode);
  return fetchJSON(url.toString(), {
    ...(token && { headers: { Authorization: `Bearer ${token}` } })
  });
}

export async function saveStrategyAllocations({ userId, token, mode, coin, data }) {
  return fetchJSON(`${API_BASE_URL}/strategies`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    },
    body: JSON.stringify({
      user_id: userId,
      mode,
      coin,
      allocations: data
    }),
  });
}

// — Positions —
export async function getPositions({ userId, token, mode }) {
  const url = new URL(`${API_BASE_URL}/positions`);
  url.searchParams.set('user_id', userId);
  url.searchParams.set('mode', mode);
  return fetchJSON(url.toString(), {
    ...(token && { headers: { Authorization: `Bearer ${token}` } })
  });
}

// — Performance —
export async function getPerformance({ userId, token, mode }) {
  const url = new URL(`${API_BASE_URL}/performance`);
  url.searchParams.set('user_id', userId);
  url.searchParams.set('mode', mode);
  return fetchJSON(url.toString(), {
    ...(token && { headers: { Authorization: `Bearer ${token}` } })
  });
}

// — User & API Keys —
export async function getUserProfile({ userId, token }) {
  return fetchJSON(`${API_BASE_URL}/user_profile?user_id=${userId}`, {
    headers: { Authorization: `Bearer ${token}` }
  });
}

export async function getApiKeys({ userId, token, exchange }) {
  return fetchJSON(
    `${API_BASE_URL}/api_keys?user_id=${userId}&exchange=${exchange}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
}

export async function saveApiKeys({ userId, token, exchange, key, secret }) {
  return fetchJSON(
    `${API_BASE_URL}/api_keys?user_id=${userId}&exchange=${exchange}`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`
      },
      body: JSON.stringify({ key, secret })
    }
  );
}