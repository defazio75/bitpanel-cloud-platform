import React, { useState, useEffect } from 'react';
import { useAuth } from "@/context/AuthContext";
import {
  getPortfolioSnapshot,
  getPrices,
  getPerformance,
  getPositions
} from "@/lib/api";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer
} from 'recharts';

const SUPPORTED_COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#d0ed57', '#a4de6c', '#8dd1e1'];

export default function PortfolioSummary({ mode }) {
  const { userId, token } = useAuth();
  const [snapshot, setSnapshot] = useState(null);
  const [prices, setPrices] = useState({});
  const [performance, setPerformance] = useState(null);
  const [positions, setPositions] = useState([]);
  const [expandedCoin, setExpandedCoin] = useState(null);

  useEffect(() => {
    if (!userId) return;
    // Fetch all data
    getPortfolioSnapshot({ userId, token, mode }).then(setSnapshot);
    getPrices({ userId, token, mode }).then(setPrices).catch(console.error);
    getPerformance({ userId, token, mode }).then(setPerformance).catch(console.error);
    getPositions({ userId, token, mode }).then(setPositions).catch(console.error);
  }, [userId, mode]);

  if (!snapshot) {
    return <p>Loading portfolio summary…</p>;
  }

  // Compute metrics
  const usdBalance = snapshot.usd_balance || 0;
  let totalValue = usdBalance;
  const allocationData = [];
  const tableData = [];

  Object.entries(snapshot.coins || {}).forEach(([coin, data]) => {
    const amount = data.balance || 0;
    const price = prices[coin]?.price || 0;
    const change = prices[coin]?.change_pct || 0;
    const usdValue = amount * price;
    if (usdValue > 0) {
      allocationData.push({ coin, value: usdValue });
      tableData.push({ coin, amount, usdValue, change });
    }
    totalValue += usdValue;
  });

  if (usdBalance > 0) {
    allocationData.push({ coin: 'USD', value: usdBalance });
  }

  // Group positions by coin
  const grouped = positions.reduce((acc, pos) => {
    const { coin } = pos;
    if (!acc[coin]) acc[coin] = [];
    acc[coin].push(pos);
    return acc;
  }, {});

  const toggleExpand = (coin) => {
    setExpandedCoin(expandedCoin === coin ? null : coin);
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>📊 Portfolio Summary ({mode.toUpperCase()})</h1>

      {/* Header Metrics */}
      <div style={{ display: 'flex', gap: '40px', margin: '20px 0' }}>
        <div>
          <h3>Total Portfolio Value</h3>
          <p style={{ fontSize: '24px' }}>${totalValue.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
        </div>
        <div>
          <h3>USD Balance</h3>
          <p style={{ fontSize: '24px' }}>${usdBalance.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
        </div>
      </div>

      {/* Holdings & Pie Chart */}
      <div style={{ display: 'flex', gap: '20px' }}>
        <div style={{ flex: 1 }}>
          <h3>💡 Coin Holdings</h3>
          {tableData.length ? (
            tableData.sort((a, b) => b.usdValue - a.usdValue).map((row) => (
              <div key={row.coin} style={{ marginBottom: 10 }}>
                <strong>{row.coin}</strong> – ${row.usdValue.toLocaleString(undefined, { minimumFractionDigits: 2 })}{' '}
                <span style={{ color: row.change >= 0 ? '#2ecc71' : '#e74c3c' }}>
                  ({row.change.toFixed(2)}%)
                </span>{' '}
                | ({row.amount.toFixed(6)}) @ ${ (prices[row.coin]?.price || 0).toLocaleString(undefined, { minimumFractionDigits: 2 }) }
              </div>
            ))
          ) : (
            <p>No coin holdings found.</p>
          )}
        </div>

        <div style={{ flex: 1 }}>
          <h3>💰 Portfolio Breakdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie data={allocationData} dataKey="value" nameKey="coin" cx="50%" cy="50%" outerRadius={100} label />
              {allocationData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={SUPPORTED_COLORS[index % SUPPORTED_COLORS.length]} />
              ))}
              <Tooltip formatter={(value) => `$${value.toLocaleString(undefined, { minimumFractionDigits: 2 })}`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Performance Metrics */}
      <div style={{ marginTop: '40px' }}>
        <h2>📊 Portfolio Performance</h2>
        {performance ? (
          <div style={{ display: 'flex', gap: '20px' }}>
            {Object.entries(performance).map(([period, data]) => (
              <div key={period} style={{ textAlign: 'center' }}>
                <h4>{period}</h4>
                <p>${data.profit.toLocaleString(undefined, { minimumFractionDigits: 2 })}</p>
                <p>{data.pct.toFixed(2)}%</p>
              </div>
            ))}
          </div>
        ) : (
          <p>Performance data not available.</p>
        )}
      </div>

      {/* Strategy Breakdown */}
      <div style={{ marginTop: '40px' }}>
        <h2>🧠 Current Strategies</h2>
        {Object.keys(grouped).length ? (
          Object.entries(grouped).map(([coin, stratArray]) => (
            <div key={coin} style={{ marginBottom: '20px' }}>
              <button
                onClick={() => toggleExpand(coin)}
                style={{
                  width: '100%',
                  textAlign: 'left',
                  background: '#f5f5f5',
                  border: 'none',
                  padding: '10px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
                {coin} Strategy Breakdown
              </button>
              {expandedCoin === coin && (
                <div style={{ padding: '10px' }}>
                  {stratArray.map((s, idx) => {
                    const value = (s.amount * (prices[s.coin]?.price || 0)) + (s.usd_held || 0);
                    const profit = s.profit_usd || 0;
                    return (
                      <p key={idx} style={{ margin: '6px 0' }}>
                        <strong>{s.strategy}</strong> | Status: <code>{s.status}</code> | Value: <strong>${value.toLocaleString(undefined, { minimumFractionDigits: 2 })}</strong> | Profit: <strong>${profit.toLocaleString(undefined, { minimumFractionDigits: 2 })}</strong>
                      </p>
                    );
                  })}
                </div>
              )}
            </div>
          ))
        ) : (
          <p>No active strategies.</p>
        )}
      </div>
    </div>
  );
}
