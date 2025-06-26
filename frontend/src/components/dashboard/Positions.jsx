// src/components/Positions.jsx
"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from "@/context/AuthContext";
import { getPositions } from '../utils/api';

export default function Positions({ mode }) {
  const { userId, token } = useAuth();
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!userId || !token) return;
    async function load() {
      try {
        const data = await getPositions({ userId, token, mode });
        setPositions(data.positions ?? data ?? []);
      } catch (err) {
        console.error('Failed to load positions:', err);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [userId, token, mode]);

  if (loading) return <p>Loading positions…</p>;
  if (!positions.length) return <p>No active positions.</p>;

  const headers = Object.keys(positions[0]);

  return (
    <div style={{ padding: 20 }}>
      <h1>📜 Current Positions ({mode.toUpperCase()})</h1>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            {headers.map(h => (
              <th
                key={h}
                style={{
                  textAlign: 'left',
                  padding: '8px',
                  borderBottom: '1px solid #ccc',
                  background: '#f9f9f9'
                }}
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {positions.map((pos, i) => (
            <tr key={i}>
              {headers.map(h => (
                <td
                  key={h}
                  style={{
                    padding: '8px',
                    borderBottom: '1px solid #eee'
                  }}
                >
                  {typeof pos[h] === 'number'
                    ? pos[h].toLocaleString(undefined, { maximumFractionDigits: 6 })
                    : String(pos[h])
                  }
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
