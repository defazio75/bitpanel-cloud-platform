// frontend/app/manual-trade/page.jsx
"use client";

import ManualTrade from "../../src/components/ManualTrade";

export default function ManualTradePage() {
  // You can pass mode dynamically if you lift state up later
  return <ManualTrade mode="paper" />;
}
