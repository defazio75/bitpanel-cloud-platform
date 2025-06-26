"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from "@/context/AuthContext";
import {
  getStrategies,
  saveStrategyAllocations,
  getPortfolioSnapshot,
} from "@/lib/api";

const MARKET_ASSUMPTIONS = ["Bullish", "Neutral", "Bearish", "Custom"];
const STRATEGIES = ["HODL", "5min RSI", "1hr RSI", "DCA Matrix", "Bollinger"];

const PRESET_ALLOCATIONS = {
  Bullish: {
    rationale:
      "Focus on high-momentum strategies with quick entry/exit logic to capitalize on upward trends.",
    allocations: {
      HODL: 40,
      "5min RSI": 20,
      "1hr RSI": 10,
      "DCA Matrix": 10,
      Bollinger: 20,
    },
  },
  Neutral: {
    rationale:
      "A balanced mix of all strategies to handle sideways markets and short-term reversals.",
    allocations: {
      HODL: 30,
      "5min RSI": 10,
      "1hr RSI": 10,
      "DCA Matrix": 40,
      Bollinger: 10,
    },
  },
  Bearish: {
    rationale:
      "Favor defensive and time-based accumulation strategies to reduce downside exposure.",
    allocations: {
      HODL: 20,
      "5min RSI": 10,
      "1hr RSI": 20,
      "DCA Matrix": 40,
      Bollinger: 10,
    },
  },
};

export default function StrategyPage({ mode }) {
  const { userId, token } = useAuth();
  const [coins, setCoins] = useState([]);
  const [balances, setBalances] = useState({});
  const [strategyData, setStrategyData] = useState({});

useEffect(() => {
  // don’t run until we have a user and a token
  if (!userId || !token) return;

  async function load() {
    // 1) portfolio snapshot
    const snap = await getPortfolioSnapshot({ userId, token, mode });
    const nonZero = Object.entries(snap.coins || {})
                          .filter(([_,d]) => d.balance > 0)
                          .map(([c]) => c);
    setCoins(nonZero);
    setBalances(snap.coins || {});

    // 2) existing strategy allocations
    const s = await getStrategies();
    setAllocs(s || {});
  }

  load();
}, [userId, token, mode]);

  // Handlers for assumption and custom sliders
  const onAssumptionChange = (coin, assumption) =>
    setStrategyData((prev) => ({
      ...prev,
      [coin]: { ...prev[coin], assumption },
    }));

  const onCustomChange = (coin, strat, val) =>
    setStrategyData((prev) => ({
      ...prev,
      [coin]: { ...prev[coin], [strat]: Number(val) },
    }));

  // Save allocations
  const save = async (coin) => {
    const cfg = strategyData[coin] || {};
    if (cfg.assumption === 'Custom') {
      const sum = STRATEGIES.reduce((acc, s) => acc + (cfg[s] || 0), 0);
      if (sum !== 100) {
        return alert(`⚠️ Custom allocations for ${coin} must sum to 100% (got ${sum}%).`);
      }
    }
    if (!confirm(`Save strategy for ${coin}?`)) return;
    try {
      await saveStrategyAllocations({ userId, token, mode, coin, data: cfg });
      alert('✅ Saved!');
    } catch (e) {
      console.error(e);
      alert('❌ Save failed');
    }
  };

  // Stop all strategies (reset to HODL)
  const stop = async (coin) => {
    if (!confirm(`Stop all strategies for ${coin}?`)) return;
    const reset = {
      assumption: 'Custom',
      HODL: 100,
      '5min RSI': 0,
      '1hr RSI': 0,
      'DCA Matrix': 0,
      Bollinger: 0,
    };
    try {
      await saveStrategyAllocations({ userId, token, mode, coin, data: reset });
      setStrategyData((prev) => ({ ...prev, [coin]: reset }));
      alert(`🛑 ${coin} reverted to 100% HODL`);
    } catch (e) {
      console.error(e);
      alert('❌ Stop failed');
    }
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>🧠 Strategy Controls ({mode.toUpperCase()})</h1>

      {coins.length === 0 && <p>No coins with non-zero balance.</p>}

      {coins.map((coin) => {
        const cfg = strategyData[coin] || {};
        const assumption = cfg.assumption || 'Neutral';
        const total = STRATEGIES.reduce((a, s) => a + (cfg[s] || 0), 0);

        return (
          <div key={coin} style={{ marginBottom: 40 }}>
            <h2>{coin}</h2>

            {/* Assumption radio buttons */}
            <div>
              {MARKET_ASSUMPTIONS.map((a) => (
                <label key={a} style={{ marginRight: 10 }}>
                  <input
                    type="radio"
                    name={`${coin}-view`}
                    value={a}
                    checked={assumption === a}
                    onChange={() => onAssumptionChange(coin, a)}
                  />{' '}
                  {a}
                </label>
              ))}
            </div>

            {/* Preset or Custom UI */}
            {assumption !== 'Custom' ? (
              <div style={{ margin: '10px 0', padding: 10, background: '#f5f5f5' }}>
                <p>{PRESET_ALLOCATIONS[assumption].rationale}</p>
                {Object.entries(PRESET_ALLOCATIONS[assumption].allocations).map(
                  ([strat, pct]) => (
                    <p key={strat}>
                      {strat}: <strong>{pct}%</strong>
                    </p>
                  )
                )}
              </div>
            ) : (
              <div style={{ margin: '10px 0' }}>
                {STRATEGIES.map((strat) => (
                  <div key={strat} style={{ marginBottom: 8 }}>
                    <label>
                      {strat}: {cfg[strat] || 0}%{' '}
                    </label>
                    <input
                      type="range"
                      min={0}
                      max={100}
                      value={cfg[strat] || 0}
                      onChange={(e) => onCustomChange(coin, strat, e.target.value)}
                    />
                  </div>
                ))}
                <p>
                  Total: {total}%{' '}
                  {total !== 100 && <span style={{ color: 'red' }}>(must be 100%)</span>}
                </p>
              </div>
            )}

            {/* Action buttons */}
            <button onClick={() => save(coin)}>💾 Save</button>
            <button onClick={() => stop(coin)} style={{ marginLeft: 10 }}>
              🛑 Stop
            </button>
          </div>
        );
      })}
    </div>
  );
}
