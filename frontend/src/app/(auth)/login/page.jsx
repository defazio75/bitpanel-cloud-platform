'use client';
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from '@/lib/firebaseClient';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await signInWithEmailAndPassword(auth, email, password);
      router.push('/dashboard/portfolio-summary');
    } catch (err) {
      setError(err.message || "Failed to sign in");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md p-8 bg-white rounded-3xl shadow-xl flex flex-col items-center">
        <h1 className="text-4xl font-extrabold text-center mb-8 text-blue-600">
          Welcome to BitPanel
        </h1>
        <form onSubmit={handleSubmit} className="space-y-4 w-full flex flex-col items-center">
          {error && (
            <div className="text-red-500 text-sm text-center w-full">{error}</div>
          )}
          <div className="w-full">
            <label className="block text-gray-700 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2 border rounded bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="you@domain.com"
            />
          </div>
          <div className="w-full">
            <label className="block text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-2 border rounded bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="••••••••"
            />
          </div>
          <div className="w-full flex justify-between text-sm">
            <Link href="/forgot-password" className="text-indigo-600 hover:text-indigo-500">
              Forgot your password?
            </Link>
            <Link href="/signup" className="text-indigo-600 hover:text-indigo-500">
              Create Account
            </Link>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-indigo-600 text-white rounded hover:bg-indigo-500 disabled:opacity-50 transition"
          >
            {loading ? 'Signing in…' : 'Log In'}
          </button>
        </form>
      </div>
    </div>
  );
}
