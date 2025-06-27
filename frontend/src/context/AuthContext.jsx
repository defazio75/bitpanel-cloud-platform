"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { onAuthStateChanged, getIdToken } from "firebase/auth";
import { auth } from '@/lib/firebaseClient'

const AuthContext = createContext({
  user: null,
  token: null,
});

export function AuthProvider({ children }) {
  const [user, setUser]     = useState(null);
  const [token, setToken]   = useState(null);

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        setUser(firebaseUser);
        const idToken = await getIdToken(firebaseUser);
        setToken(idToken);
      } else {
        setUser(null);
        setToken(null);
      }
    });
    return unsub;
  }, []);

  return (
    <AuthContext.Provider value={{ user, token }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
