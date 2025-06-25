import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { signOut } from 'firebase/auth';
import { auth } from '../../lib/firebaseClient';

const pages = ['Portfolio', 'Strategies', 'Positions', 'Performance', 'Manual Trade', 'Settings'];

export default function Sidebar({ userName, totalPortfolio, availableUSD, onPageSelect, activePage, mode, setMode }) {
  const router = useRouter();
  const [resetting, setResetting] = useState(false);
  const [resetError, setResetError] = useState(null);

  const handleLogout = async () => {
    await signOut(auth);
    router.push('/login');
  };

  const toggleMode = () => {
    setMode(mode === 'paper' ? 'live' : 'paper');
  };

  // New reset paper account handler
  const handleResetPaper = async () => {
    setResetting(true);
    setResetError(null);
    try {
      const res = await fetch('/api/reset-paper-account', { method: 'POST' });
      if (!res.ok) throw new Error('Failed to reset paper account');
      alert('Paper account reset successfully!');
      router.refresh();
    } catch (e) {
      setResetError(e.message);
    } finally {
      setResetting(false);
    }
  };

  return (
    <div style={{
      width: '280px',
      height: '100vh',
      overflowY: 'auto',
      backgroundColor: '#1a202c',
      color: 'white',
      padding: '20px',
      boxSizing: 'border-box',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'flex-start',
      gap: '20px',
      fontFamily: 'Arial, sans-serif',
      fontWeight: '500'
    }}>
      <div style={{ fontSize: '24px', marginBottom: '20px' }}>
        🚀 <strong>BitPanel</strong>
      </div>

      <div style={{ fontSize: '14px', opacity: 0.7 }}>
        👤 Logged in as:<br />
        <strong>{userName}</strong>
      </div>

      <button
        onClick={handleLogout}
        style={{
          backgroundColor: '#e53e3e',
          color: 'white',
          border: 'none',
          padding: '8px 12px',
          borderRadius: '6px',
          cursor: 'pointer',
          width: '100%',
          fontWeight: '600'
        }}
      >
        Logout
      </button>

      {/* Mode toggle */}
      <div style={{ marginTop: '10px' }}>
        <label style={{ fontWeight: '600', marginBottom: '8px', display: 'block' }}>Mode</label>
        <button
          onClick={toggleMode}
          style={{
            width: '100%',
            padding: '8px',
            backgroundColor: mode === 'live' ? '#38a169' : '#718096',
            border: 'none',
            borderRadius: '6px',
            color: 'white',
            fontWeight: '700',
            cursor: 'pointer',
            userSelect: 'none',
            transition: 'background-color 0.3s ease'
          }}
          aria-pressed={mode === 'live'}
          title={`Switch to ${mode === 'live' ? 'Paper' : 'Live'} Mode`}
        >
          {mode === 'live' ? 'Live Mode' : 'Paper Mode'}
        </button>
      </div>

      {/* Reset Paper Account button only shown in paper mode */}
      {mode === 'paper' && (
        <>
          <button
            onClick={handleResetPaper}
            disabled={resetting}
            style={{
              marginTop: '12px',
              padding: '8px 12px',
              width: '100%',
              backgroundColor: '#e53e3e',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: resetting ? 'not-allowed' : 'pointer',
              fontWeight: '600'
            }}
          >
            {resetting ? 'Resetting...' : 'Reset Paper Account'}
          </button>
          {resetError && <div style={{ color: 'red', marginTop: 6 }}>{resetError}</div>}
        </>
      )}

      <hr style={{ borderColor: 'rgba(255,255,255,0.2)', marginTop: '30px' }} />

      <div style={{ fontSize: '18px' }}>
        💰 <strong>Portfolio Summary</strong>
      </div>

      <div style={{ fontSize: '16px', marginTop: '10px' }}>
        Total Portfolio: <br />
        <span style={{ fontWeight: '700' }}>${totalPortfolio}</span>
      </div>

      <div style={{ fontSize: '16px', marginTop: '10px' }}>
        Available USD: <br />
        <span style={{ fontWeight: '700' }}>${availableUSD}</span>
      </div>

      <hr style={{ borderColor: 'rgba(255,255,255,0.2)', marginTop: '30px' }} />

      <nav>
        {pages.map(page => (
          <div
            key={page}
            onClick={() => onPageSelect(page)}
            style={{
              padding: '10px 15px',
              marginBottom: '6px',
              cursor: 'pointer',
              borderRadius: '6px',
              backgroundColor: activePage === page ? '#2d3748' : 'transparent',
              fontWeight: activePage === page ? '700' : '500',
              userSelect: 'none',
              transition: 'background-color 0.2s ease'
            }}
            onMouseEnter={e => e.currentTarget.style.backgroundColor = activePage === page ? '#2d3748' : '#4a5568'}
            onMouseLeave={e => e.currentTarget.style.backgroundColor = activePage === page ? '#2d3748' : 'transparent'}
          >
            {page}
          </div>
        ))}
      </nav>
    </div>
  );
}