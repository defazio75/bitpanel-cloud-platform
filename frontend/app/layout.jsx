// app/layout.jsx
"use client";

import React, { useState } from 'react';
import { AuthProvider } from '../src/context/AuthContext';

import Sidebar from '../src/components/Sidebar';
import PortfolioSummary from '../src/components/PortfolioSummary';
import StrategyPage from '../src/components/strategy';
import Positions from '../src/components/Positions';
import Performance from '../src/components/Performance';
import ManualTrade from '../src/components/ManualTrade';
import Settings from '../src/components/Settings';

const pages = ['Portfolio', 'Manual Trade', 'Strategies', 'Positions', 'Performance', 'Settings'];

export default function RootLayout() {
  const [activePage, setActivePage] = useState('Portfolio');
  const [mode, setMode]         = useState('paper');

  const renderPage = () => {
    switch (activePage) {
      case "Portfolio":
        return <PortfolioSummary mode={mode} />;

      case "Manual Trade":
        return <ManualTrade mode={mode} />;

      case "Strategies":
        return <StrategyPage mode={mode} />;

      case "Positions":
        return <Positions mode={mode} />;

      case "Performance":
        return <Performance mode={mode} />;

      case "Settings":
        return <Settings mode={mode} />;

      default:
        return (
          <div style={{ padding: '20px', color: '#555' }}>
            Page “{activePage}” not yet implemented.
          </div>
        );
    }
  };

  return (
    <AuthProvider>
      <html lang="en">
        <body style={{ margin: 0, padding: 0, fontFamily: 'Arial, sans-serif' }}>
          <div style={{ display: 'flex', height: '100vh' }}>
            <Sidebar
              userName="Dave DeFazio"
              totalPortfolio="101,246.89"
              availableUSD="13,250.89"
              activePage={activePage}
              onPageSelect={setActivePage}
              mode={mode}
              setMode={setMode}
              pages={pages}
            />
            <main
              style={{
                flexGrow: 1,
                padding: 20,
                backgroundColor: '#f0f2f5',
                overflowY: 'auto'
              }}
            >
              {renderPage()}
            </main>
          </div>
        </body>
      </html>
    </AuthProvider>
  );
}