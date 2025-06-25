// src/components/ManualTrade.jsx
"use client";

import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import { getPrices, executeManualTrade } from "../utils/api";
import styles from "./ManualTrade.module.css"; // optional, for styling

const SUPPORTED_COINS = ["BTC", "ETH", "SOL", "DOT", "XRP", "LINK"];

export default function ManualTrade({ mode }) {
  const { userId, token } = useAuth(); 
  const [selectedCoin, setSelectedCoin] = useState("");
  const [price, setPrice] = useState(0);
  const [usdAmount, setUsdAmount] = useState("");
  const [isBuying, setIsBuying] = useState(true);
  const [loading, setLoading] = useState(false);

  // Whenever the user picks a coin, fetch its current price
  useEffect(() => {
    if (!selectedCoin) return;
    getPrices()
      .then((data) => {
        setPrice(data[selectedCoin] ?? 0);
      })
      .catch((err) => console.error("getPrices error:", err));
  }, [selectedCoin]);

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
      // Optionally clear inputs:
      setUsdAmount("");
    } catch (err) {
      console.error("executeManualTrade error:", err);
      alert(`❌ Trade failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>💸 Manual Trade</h1>

      <label className={styles.label}>Select Coin</label>
      <select
        className={styles.select}
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
        <p className={styles.price}>
          Price: {price > 0 ? `$${price.toFixed(2)}` : "Loading…"}
        </p>
      )}

      <label className={styles.label}>Amount (USD)</label>
      <input
        type="number"
        className={styles.input}
        placeholder="e.g. 100.00"
        value={usdAmount}
        onChange={(e) => setUsdAmount(e.target.value)}
      />

      <div className={styles.toggleRow}>
        <button
          className={`${styles.toggleBtn} ${
            isBuying ? styles.active : ""
          }`}
          onClick={() => setIsBuying(true)}
        >
          Buy
        </button>
        <button
          className={`${styles.toggleBtn} ${
            !isBuying ? styles.active : ""
          }`}
          onClick={() => setIsBuying(false)}
        >
          Sell
        </button>
      </div>

      <button
        className={styles.confirmBtn}
        onClick={handleConfirm}
        disabled={
          loading ||
          !selectedCoin ||
          !usdAmount ||
          parseFloat(usdAmount) <= 0 ||
          price <= 0
        }
      >
        {loading ? "Working…" : `Confirm ${isBuying ? "Buy" : "Sell"}`}
      </button>
    </div>
  );
}
