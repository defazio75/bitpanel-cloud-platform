// src/app/dashboard/layout.jsx
'use client';

import React, { useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import Sidebar from '@/components/dashboard/Sidebar';
import Navbar from '@/components/dashboard/Navbar';

export default function DashboardLayout({ children }) {
  const [mode, setMode] = useState('paper');
  const path = usePathname();
  const router = useRouter();

  const pages = [
    { label: 'Portfolio',    path: '/dashboard/portfolio-summary' },
    { label: 'Manual Trade', path: '/dashboard/manual-trade' },
    { label: 'Strategies',   path: '/dashboard/strategies' },
    { label: 'Positions',    path: '/dashboard/current-positions' },
    { label: 'Performance',  path: '/dashboard/performance' },
    { label: 'Settings',     path: '/dashboard/settings' },
  ];

  return (
    <div className="flex h-screen">
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
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="p-6 bg-white flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
