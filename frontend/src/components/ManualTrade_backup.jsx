"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getPrices, executeManualTrade } from "../utils/api";
import { useAuth } from "../context/AuthContext";

const SUPPORTED_COINS = ["BTC", "ETH", "SOL", "DOT", "XRP", "LINK"];

export default function ManualTrade({ mode }) {
  const { user, token } = useAuth();
  const router = useRouter();

  const [prices, setPrices] = useState({});
  const [selectedCoin, setSelectedCoin] = useState("");
  const [action, setAction] = useState("buy");
  const [usdAmount, setUsdAmount] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch live prices on mount
  useEffect(() => {
    async function loadPrices() {
      try {
        const data = await getPrices();
        setPrices(data || {});
      } catch (err) {
        console.error("Failed to load prices", err);
      }
    }
    loadPrices();
  }, []);

  // Calculate estimated coin quantity
  const estimatedQty = selectedCoin && prices[selectedCoin]
    ? (parseFloat(usdAmount) / prices[selectedCoin]).toFixed(6)
    : "0.000000";

  const handleConfirm = async () => {
    if (!selectedCoin || !usdAmount) return;
    setLoading(true);
    setError(null);
    try {
      const tradeData = {
        userId: user.uid,
        token,
        mode,
        coin: selectedCoin,
        action,
        amountUsd: parseFloat(usdAmount)
      };

      const result = await executeManualTrade(tradeData);
      // On success, you might refresh or navigate
      router.refresh();
      alert(`✅ ${action.toUpperCase()} ${estimatedQty} ${selectedCoin} @ $${prices[selectedCoin].toFixed(2)} successful.`);
      setUsdAmount("");
    } catch (err) {
      console.error("Trade failed", err);
      setError(err.message || "Trade failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: 'auto', padding: 20 }}>
      <h1>💸 Manual Trade</h1>
      <p>Select coin, Buy/Sell, and USD amount:</p>

      <label>Coin</label>
      <select
        value={selectedCoin}
        onChange={e => setSelectedCoin(e.target.value)}
        style={{ width: '100%', padding: '8px', marginBottom: '12px' }}
      >
        <option value="">-- Select Coin --</option>
        {SUPPORTED_COINS.map(coin => (
          <option key={coin} value={coin}>{coin}</option>
        ))}
      </select>

      <label>Action</label>
      <select
        value={action}
        onChange={e => setAction(e.target.value)}
        style={{ width: '100%', padding: '8px', marginBottom: '12px' }}
      >
        <option value="buy">Buy</option>
        <option value="sell">Sell</option>
      </select>

      <label>Amount (USD)</label>
      <input
        type="number"
        value={usdAmount}
        onChange={e => setUsdAmount(e.target.value)}
        placeholder="0.00"
        style={{ width: '100%', padding: '8px', marginBottom: '12px' }}
      />

      <div style={{ marginBottom: '12px' }}>
        Estimated: <strong>{estimatedQty} {selectedCoin}</strong>
      </div>

      {error && <div style={{ color: 'red', marginBottom: '12px' }}>{error}</div>}

      <button
        onClick={handleConfirm}
        disabled={!selectedCoin || !usdAmount || loading}
        style={{
          width: '100%',
          padding: '10px',
          backgroundColor: '#3182ce',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: loading ? 'not-allowed' : 'pointer'
        }}
      >
        {loading ? 'Processing...' : `Confirm ${action.charAt(0).toUpperCase() + action.slice(1)}`}
      </button>
    </div>
  );
}
