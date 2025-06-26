// src/app/error.jsx

'use client'; // Required for error boundaries

import { useEffect } from 'react';

export default function GlobalError({ error, reset }) {
  useEffect(() => {
    console.error('💥 Unhandled error:', error);
  }, [error]);

  return (
    <html>
      <body className="flex flex-col items-center justify-center min-h-screen text-center bg-red-50 px-4">
        <h1 className="text-3xl font-bold text-red-600 mb-4">Something went wrong</h1>
        <p className="text-gray-700 mb-6">
          An unexpected error occurred. Please try again or contact support.
        </p>
        <button
          onClick={() => reset()}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Try Again
        </button>
      </body>
    </html>
  );
}
