// src/components/Settings.jsx
"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import {
  getUserProfile,
  getApiKeys,
  saveApiKeys
} from "@/lib/api";

const EXCHANGES = ["kraken", "binance", "coinbase"];

export default function Settings() {
  const router = useRouter();
  const { userId, token } = useAuth();
  const [profile, setProfile] = useState(null);
  const [exchange, setExchange] = useState("kraken");
  const [keys, setKeys] = useState({ key: "", secret: "" });
  const [editing, setEditing] = useState(false);

  // Load user profile (email, plan, etc.)
  useEffect(() => {
    if (!userId || !token) return;
    getUserProfile({ userId, token })
      .then(setProfile)
      .catch(console.error);
  }, [userId, token]);

  // Load existing API keys
  useEffect(() => {
    if (!userId || !token) return;
    getApiKeys({ userId, token, exchange })
      .then(data => {
        setKeys({
          key: data.key || "",
          secret: data.secret || ""
        });
      })
      .catch(() => setKeys({ key: "", secret: "" }));
  }, [userId, token, exchange]);

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      await saveApiKeys({
        userId,
        token,
        exchange,
        key: keys.key,
        secret: keys.secret
      });
      setEditing(false);
      alert("✅ Keys saved!");
    } catch (err) {
      console.error(err);
      alert("❌ Save failed");
    }
  };

  if (!profile) {
    return <p>Loading settings…</p>;
  }

  const isPaid = ["admin", "customer"].includes(profile.role);

  return (
    <div style={{ padding: 20 }}>
      <h1>⚙️ Settings</h1>

      {/* Account Info */}
      <section>
        <h2>👤 Account Info</h2>
        <p><strong>Email:</strong> {profile.email}</p>
        <p><strong>User ID:</strong> {userId}</p>
      </section>

      <hr />

      {/* Subscription */}
      <section>
        <h2>💳 Subscription</h2>
        {isPaid ? (
          <p>✅ {profile.planName || "Pro Plan"}</p>
        ) : (
          <p>
            🚫 Free version —{" "}
            <button onClick={() => router.push("/upgrade")}>
              Upgrade to Pro
            </button>
          </p>
        )}
      </section>

      <hr />

      {/* API Keys */}
      <section>
        <h2>🔐 Exchange API Keys</h2>
        <label>
          Exchange:
          <select
            value={exchange}
            onChange={(e) => {
              setExchange(e.target.value);
              setEditing(false);
            }}
          >
            {EXCHANGES.map((ex) => (
              <option key={ex} value={ex}>
                {ex.charAt(0).toUpperCase() + ex.slice(1)}
              </option>
            ))}
          </select>
        </label>

        {!editing ? (
          <div style={{ marginTop: 12 }}>
            {keys.key && keys.secret ? (
              <div>
                <p>✅ Keys saved for {exchange}</p>
                <button onClick={() => setEditing(true)}>
                  ✏️ Edit Keys
                </button>
              </div>
            ) : (
              <button onClick={() => setEditing(true)}>
                ➕ Add Keys for {exchange}
              </button>
            )}
          </div>
        ) : (
          <form onSubmit={handleSave} style={{ marginTop: 12 }}>
            <div>
              <label>
                API Key
                <input
                  type="text"
                  value={keys.key}
                  onChange={(e) =>
                    setKeys((k) => ({ ...k, key: e.target.value }))
                  }
                  required
                  style={{ width: "100%", margin: "4px 0" }}
                />
              </label>
            </div>
            <div>
              <label>
                API Secret
                <input
                  type="password"
                  value={keys.secret}
                  onChange={(e) =>
                    setKeys((k) => ({ ...k, secret: e.target.value }))
                  }
                  required
                  style={{ width: "100%", margin: "4px 0" }}
                />
              </label>
            </div>
            <button type="submit" style={{ marginRight: 8 }}>
              💾 Save Keys
            </button>
            <button type="button" onClick={() => setEditing(false)}>
              ❌ Cancel
            </button>
          </form>
        )}
      </section>
    </div>
);
}
