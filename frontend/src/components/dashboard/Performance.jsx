"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from "@/context/AuthContext";
import { getPerformance } from '../utils/api';

export default function PerformancePage({ mode }) {
  const { userId, token } = useAuth();
  const [performanceData, setPerformanceData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      setLoading(true);
      setError(null);
      try {
        const data = await getPerformance({ userId, token, mode });
        setPerformanceData(data);
      } catch (err) {
        console.error('Failed to load performance:', err);
        setError('Failed to load performance data.');
      } finally {
        setLoading(false);
      }
    }
    if (userId) fetchData();
  }, [userId, token, mode]);

  if (loading) return <div style={{ padding: 20 }}>Loading performance…</div>;
  if (error) return <div style={{ padding: 20, color: 'red' }}>{error}</div>;

  // Destructure with defaults
  const {
    total = { daily: 'N/A', weekly: 'N/A', monthly: 'N/A', yearly: 'N/A' },
    individual = {},
    stacking = {},
  } = performanceData || {};

  return (
    <div style={{ padding: 20 }}>
      <h1>📈 Performance Dashboard</h1>

      <section>
        <h2>Total Portfolio Performance</h2>
        <div style={{ display: 'flex', gap: '20px' }}>
          <div><strong>Daily:</strong> {total.daily}</div>
          <div><strong>Weekly:</strong> {total.weekly}</div>
          <div><strong>Monthly:</strong> {total.monthly}</div>
          <div><strong>Yearly:</strong> {total.yearly}</div>
        </div>
      </section>

      <hr style={{ margin: '20px 0' }} />

      <section>
        <h2>Individual Coin Performance</h2>
        {Object.entries(individual).map(([coin, stats]) => (
          <div key={coin} style={{ marginBottom: 8 }}>
            {coin}: {stats.daily} daily, {stats.monthly} monthly
          </div>
        ))}
      </section>

      <hr style={{ margin: '20px 0' }} />

      <section>
        <h2>Coin Stacking Progress</h2>
        {Object.entries(stacking).map(([coin, amt]) => (
          <div key={coin} style={{ marginBottom: 8 }}>
            {coin}: {amt} accumulated
          </div>
        ))}
      </section>

      <hr style={{ margin: '20px 0' }} />

      <section>
        <h2>Coming Soon: Strategy Performance vs HODL</h2>
        <div style={{ fontStyle: 'italic', color: '#666' }}>
          This section will compare strategy performance against passive HODL performance.
        </div>
      </section>
    </div>
  );
}
