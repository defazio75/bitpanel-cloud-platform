// src/components/ManualTrade.jsx
"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { getPrices, executeManualTrade } from "@/utils/api"

const SUPPORTED_COINS = ["BTC", "ETH", "SOL", "DOT", "XRP", "LINK"];

export default function ManualTrade({ mode }) {
  const { userId, token } = useAuth();
  const [selectedCoin, setSelectedCoin] = useState("");
  const [price, setPrice] = useState(0);
  const [usdAmount, setUsdAmount] = useState("");
  const [isBuying, setIsBuying] = useState(true);
  const [loading, setLoading] = useState(false);


  // Fetch price when coin changes
  useEffect(() => {
    if (!selectedCoin || !userId) return;
    getPrices(userId)
      .then((data) => {
        setPrice(data[selectedCoin] ?? 0);
      })
      .catch(err => console.error("getPrices error:", err));
  }, [selectedCoin, userId]);

  const handleConfirm = async () => {
    if (!selectedCoin || !usdAmount || price <= 0) return;
    const quantity = parseFloat(usdAmount) / price;

    const tradeData = {
      user_id: userId,
      token,
      mode,                      // "paper" or "live"
      bot_name: "ManualTrade",
      action: isBuying ? "buy" : "sell",
      coin: selectedCoin,
      amount: quantity,
      price,
    };

    setLoading(true);
    try {
      const result = await executeManualTrade(tradeData);
      alert(`✅ Trade successful:\n${JSON.stringify(result)}`);
      setUsdAmount("");
    } catch (err) {
      console.error("executeManualTrade error:", err);
      alert(`❌ Trade failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: 'auto', padding: 20 }}>
      <h1>💸 Manual Trade</h1>

      <label>Select Coin</label>
      <select
        style={{ width: '100%', padding: 8, margin: '8px 0' }}
        value={selectedCoin}
        onChange={(e) => setSelectedCoin(e.target.value)}
      >
        <option value="">-- choose --</option>
        {SUPPORTED_COINS.map((c) => (
          <option key={c} value={c}>
            {c}
          </option>
        ))}
      </select>

      {selectedCoin && (
        <p>Price: {price > 0 ? `$${price.toFixed(2)}` : 'Loading…'}</p>
      )}

      <label>Amount (USD)</label>
      <input
        type="number"
        style={{ width: '100%', padding: 8, margin: '8px 0' }}
        placeholder="e.g. 100.00"
        value={usdAmount}
        onChange={(e) => setUsdAmount(e.target.value)}
      />

      <div style={{ display: 'flex', gap: 8, margin: '12px 0' }}>
        <button
          style={{ flex: 1, padding: 10, background: isBuying ? '#3182ce' : '#e2e8f0', color: isBuying ? 'white' : 'black', border: 'none', borderRadius: 4 }}
          onClick={() => setIsBuying(true)}
        >
          Buy
        </button>
        <button
          style={{ flex: 1, padding: 10, background: !isBuying ? '#e53e3e' : '#e2e8f0', color: !isBuying ? 'white' : 'black', border: 'none', borderRadius: 4 }}
          onClick={() => setIsBuying(false)}
        >
          Sell
        </button>
      </div>

      <button
        onClick={handleConfirm}
        disabled={
          loading ||
          !selectedCoin ||
          !usdAmount ||
          parseFloat(usdAmount) <= 0 ||
          price <= 0
        }
        style={{
          width: '100%',
          padding: 12,
          background: '#2d3748',
          color: 'white',
          border: 'none',
          borderRadius: 4,
          cursor: loading ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? 'Working…' : `Confirm ${isBuying ? 'Buy' : 'Sell'}`}
      </button>
    </div>
  );
}
