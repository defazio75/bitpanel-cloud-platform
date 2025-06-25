"use client"; // needed in Next.js 13 app dir for client components

import { useState } from "react";
import app from "../lib/firebaseClient"; // adjust path if you saved elsewhere
import { getAuth, signInWithEmailAndPassword } from "firebase/auth";
import { useRouter } from "next/navigation";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState("");
  const router = useRouter();

  const auth = getAuth(app);

  const handleLogin = async (e) => {
    e.preventDefault();
    setErrorMsg("");

    try {
      await signInWithEmailAndPassword(auth, email, password);
      router.push("/"); // redirect to home/dashboard on success
    } catch (error) {
      console.error("Firebase login error:", error);
      setErrorMsg(error.message);
    }
  };

  return (
    <div style={{ maxWidth: 400, margin: "auto", padding: "2rem" }}>
      <h1>Login to BitPanel</h1>
      <form onSubmit={handleLogin}>
        <label>Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={{ width: "100%", marginBottom: "1rem" }}
        />
        <label>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={{ width: "100%", marginBottom: "1rem" }}
        />
        {errorMsg && <p style={{ color: "red" }}>{errorMsg}</p>}
        <button type="submit" style={{ width: "100%", padding: "0.5rem" }}>
          Log In
        </button>
      </form>
    </div>
  );
}