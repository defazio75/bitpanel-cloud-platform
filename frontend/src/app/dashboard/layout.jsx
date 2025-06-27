'use client';
import Sidebar from '@/components/dashboard/Sidebar';
import Navbar  from '@/components/dashboard/Navbar';

export default function DashboardLayout({ children }) {
  return (
    <div className="flex min-h-screen bg-gray-100">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="p-6 bg-white flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
}
