// src/app/page.jsx

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/login');
  }, [router]);

  return (
    <main className="flex items-center justify-center min-h-screen text-center p-6">
      <p className="text-gray-500 text-lg">Redirecting to login...</p>
    </main>
  );
}
