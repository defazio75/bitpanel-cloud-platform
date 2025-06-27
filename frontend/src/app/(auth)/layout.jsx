// src/app/(auth)/layout.jsx
'use client';

export default function AuthLayout({ children }) {
  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md p-8 bg-white rounded-3xl shadow-xl">
        {children}
      </div>
    </div>
  );
}
