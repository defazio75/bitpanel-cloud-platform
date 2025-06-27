'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '@/lib/firebaseClient';
import LoginForm from '@/components/auth/LoginForm';
import Link from 'next/link';

export default function LoginPage() {
  const router = useRouter();

  const handleLogin = async ({ email, password }) => {
    // delegate to Firebase
    await signInWithEmailAndPassword(auth, email, password);
    router.push('/dashboard/portfolio-summary');
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="w-full max-w-md p-8 bg-white rounded-3xl shadow-xl">
        <h1 className="text-4xl font-extrabold text-center mb-8 text-blue-600">
          Welcome to BitPanel
        </h1>

        <LoginForm onSubmit={handleLogin} />

        <div className="mt-6 flex justify-between text-sm text-gray-600">
          <Link href="/forgot-password" className="hover:underline">
            Forgot Password?
          </Link>
          <Link href="/signup" className="hover:underline">
            Create Account
          </Link>
        </div>
      </div>
    </div>
  );
}
