// src/components/auth/SignupForm.jsx

'use client';

import { useState } from 'react';

export default function SignupForm({ onSubmit }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleSubmit = e => {
    e.preventDefault();
    if (password !== confirmPassword) {
      alert('Passwords do not match.');
      return;
    }

    if (onSubmit) {
      onSubmit({ email, password });
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 w-full max-w-sm mx-auto">
      <h2 className="text-2xl font-semibold text-center mb-6">Create Your BitPanel Account</h2>

      <input
        type="email"
        placeholder="Email"
        className="w-full p-3 border border-gray-300 rounded"
        value={email}
        onChange={e => setEmail(e.target.value)}
        required
      />

      <input
        type="password"
        placeholder="Password"
        className="w-full p-3 border border-gray-300 rounded"
        value={password}
        onChange={e => setPassword(e.target.value)}
        required
      />

      <input
        type="password"
        placeholder="Confirm Password"
        className="w-full p-3 border border-gray-300 rounded"
        value={confirmPassword}
        onChange={e => setConfirmPassword(e.target.value)}
        required
      />

      <button
        type="submit"
        className="w-full bg-green-600 text-white py-3 rounded hover:bg-green-700"
      >
        Sign Up
      </button>
    </form>
  );
}
