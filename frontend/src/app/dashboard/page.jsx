// src/app/page.jsx

import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white text-center px-4">
      <h1 className="text-4xl font-bold mb-4">🚀 Welcome to BitPanel</h1>
      <p className="text-gray-600 mb-6 max-w-md">
        Automate your crypto portfolio with strategy bots and real-time tracking.
      </p>
      <div className="flex gap-4">
        <Link href="/login" className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          Log In
        </Link>
        <Link href="/signup" className="px-6 py-2 border border-blue-600 text-blue-600 rounded hover:bg-blue-100">
          Create Account
        </Link>
      </div>
    </div>
  );
}
