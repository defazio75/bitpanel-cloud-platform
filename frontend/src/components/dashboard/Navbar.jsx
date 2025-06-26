// src/components/dashboard/Navbar.jsx

'use client';

import { useAuth } from '@/hooks/useAuth';
import Button from '@/components/ui/Button';

export default function Navbar() {
  const { user, logout } = useAuth();

  return (
    <header className="w-full bg-white shadow-sm px-6 py-4 flex justify-between items-center border-b">
      <h1 className="text-xl font-semibold text-blue-600">BitPanel</h1>

      <div className="flex items-center gap-4">
        {user && (
          <span className="text-sm text-gray-600">
            Logged in as <strong>{user.email}</strong>
          </span>
        )}
        {user && (
          <Button className="bg-red-500 hover:bg-red-600" onClick={logout}>
            Log Out
          </Button>
        )}
      </div>
    </header>
  );
}
