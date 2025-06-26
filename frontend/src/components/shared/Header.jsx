// src/components/shared/Header.jsx

import Link from 'next/link';

export default function Header() {
  return (
    <header className="w-full bg-white border-b shadow-sm py-4 px-6 flex justify-between items-center">
      <Link href="/" className="text-xl font-bold text-blue-600">
        BitPanel
      </Link>
      <nav className="flex gap-4 text-sm text-gray-700">
        <Link href="/login" className="hover:underline">Login</Link>
        <Link href="/signup" className="hover:underline">Sign Up</Link>
      </nav>
    </header>
  );
}
