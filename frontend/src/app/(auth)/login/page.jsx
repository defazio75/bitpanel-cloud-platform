'use client';
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { signInWithEmailAndPassword } from "firebase/auth";
import { auth } from '../../../lib/firebaseClient';

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
  <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center">
    <div className="w-full max-w-md bg-white rounded-2xl shadow-2xl px-8 py-10 flex flex-col items-center">
      <div className="flex items-center justify-center mb-8 gap-3">
        <img
          src="/logo.svg"
          alt="BitPanel Logo"
          className="w-10 h-10"
          style={{ objectFit: "contain" }}
        />
        <h1 className="text-3xl font-bold text-gray-900 text-center">
          Welcome to BitPanel
        </h1>
      </div>  
      {error && (
        <div className="mb-4 text-red-500 text-sm text-center">
          {error}
        </div>
      )}
      <form onSubmit={handleSubmit} className="w-full space-y-6">
        <div>
          <label className="block text-gray-700 mb-1">Email</label>
          <input
            type="email"
            className="w-full px-4 py-2 rounded-md border border-gray-300 bg-gray-50 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="you@domain.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-gray-700 mb-1">Password</label>
          <input
            type="password"
            className="w-full px-4 py-2 rounded-md border border-gray-300 bg-gray-50 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <div className="flex items-center justify-between text-sm">
          <Link href="/forgot-password" className="text-indigo-500 hover:text-indigo-600">
            Forgot your password?
          </Link>
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 rounded-lg text-white font-semibold transition"
        >
          {loading ? "Signing in…" : "Log In"}
        </button>
      </form>
      <p className="mt-8 text-center text-gray-500">
        Need an account?{" "}
        <Link href="/signup" className="text-indigo-500 hover:text-indigo-600 font-semibold">
          Create Account
        </Link>
      </p>
    </div>
  </div>
);
} 
