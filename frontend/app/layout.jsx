// frontend/app/layout.jsx
"use client";
import "./globals.css";
import React, { useState } from "react";
import { AuthProvider } from "../src/context/AuthContext";
import Sidebar from "../src/components/Sidebar";
import { usePathname, useRouter } from "next/navigation";

export default function RootLayout({ children }) {
  const [mode, setMode] = useState("paper");
  const path = usePathname();
  const router = useRouter();

  const pages = [
    { label: "Portfolio",   path: "/dashboard" },
    { label: "Manual Trade",path: "/manual-trade" },
    { label: "Strategies",  path: "/strategies" },
    { label: "Positions",   path: "/positions" },
    { label: "Performance", path: "/performance" },
    { label: "Settings",    path: "/settings" },
  ];

  return (
    <AuthProvider>
      <html lang="en">
        <body className="flex h-screen bg-gray-100 font-sans">
          <Sidebar
            userName="Dave DeFazio"
            totalPortfolio="101,246.89"
            availableUSD="13,250.89"
            pages={pages}
            activePage={path}
            onPageSelect={(p) => router.push(p)}
            mode={mode}
            setMode={setMode}
          />
          <main className="flex-1 p-6 bg-white overflow-y-auto">
            {children}  {/* routed page components render here */}
          </main>
        </body>
      </html>
    </AuthProvider>
  );
}
