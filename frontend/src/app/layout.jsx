// src/app/layout.jsx
import '@/styles/globals.css';
import { AuthProvider } from '@/context/AuthContext';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="bg-gray-100 font-sans min-h-screen">
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
