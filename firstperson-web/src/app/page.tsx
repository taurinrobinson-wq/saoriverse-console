"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";

type View = "splash" | "login" | "register";

export default function Home() {
  const [view, setView] = useState<View>("splash");
  const [showLogo, setShowLogo] = useState(true);
  const [logoMoving, setLogoMoving] = useState(false);
  const [loginUsername, setLoginUsername] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [registerData, setRegisterData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    username: "",
    password: "",
  });

  useEffect(() => {
    const timer = setTimeout(() => {
      setLogoMoving(true);
    }, 1500);
    return () => clearTimeout(timer);
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Call auth.py edge function
      const response = await fetch("/api/auth", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: loginUsername,
          password: loginPassword,
        }),
      });
      if (response.ok) {
        // Navigate to authenticated-saori
        window.location.href = "/chat";
      }
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Call auth-manager edge function
      const response = await fetch("/api/auth-manager", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(registerData),
      });
      if (response.ok) {
        setView("login");
      }
    } catch (error) {
      console.error("Registration failed:", error);
    }
  };

  const handleDemo = async () => {
    try {
      // Load saori-fixed edge function
      window.location.href = "/chat?demo=true";
    } catch (error) {
      console.error("Demo load failed:", error);
    }
  };

  return (
    <main className="min-h-screen bg-white flex items-center justify-center">
      {view === "splash" && (
        <motion.div className="flex flex-col items-center gap-8">
          {/* Logo */}
          <motion.div
            animate={
              logoMoving
                ? {
                    opacity: 0.3,
                    scale: 0.3,
                    y: -80,
                  }
                : { opacity: 1, scale: 1, y: 0 }
            }
            transition={{ duration: 1.2, ease: "easeInOut" }}
            className="relative w-48 h-48"
          >
            <Image
              src="/graphics/FirstPerson-Logo_cropped.svg"
              alt="FirstPerson Logo"
              fill
              className="object-contain"
            />
          </motion.div>

          {/* Text that appears after logo dissolve */}
          {logoMoving && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="text-center"
            >
              <h1 className="text-3xl font-bold text-slate-900 mb-2">
                Personal Companion
              </h1>

              {/* Buttons */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.6 }}
                className="flex gap-4 mt-12 flex-col sm:flex-row"
              >
                <button
                  onClick={() => setView("login")}
                  className="px-8 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
                >
                  Login
                </button>
                <button
                  onClick={() => setView("register")}
                  className="px-8 py-3 bg-slate-200 text-slate-900 rounded-lg font-semibold hover:bg-slate-300 transition-colors"
                >
                  Register
                </button>
                <button
                  onClick={handleDemo}
                  className="px-8 py-3 bg-emerald-600 text-white rounded-lg font-semibold hover:bg-emerald-700 transition-colors"
                >
                  Demo
                </button>
              </motion.div>
            </motion.div>
          )}
        </motion.div>
      )}

      {view === "login" && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-md px-6"
        >
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-6">Login</h2>

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={loginUsername}
                  onChange={(e) => setLoginUsername(e.target.value)}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>

              <button
                type="submit"
                className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition-colors mt-6"
              >
                Sign In
              </button>
            </form>

            <button
              onClick={() => setView("splash")}
              className="w-full mt-4 px-4 py-2 text-slate-600 font-medium hover:text-slate-900 transition-colors"
            >
              Back
            </button>
          </div>
        </motion.div>
      )}

      {view === "register" && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-md px-6"
        >
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-8">
            <h2 className="text-2xl font-bold text-slate-900 mb-6">Register</h2>

            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  First Name
                </label>
                <input
                  type="text"
                  value={registerData.firstName}
                  onChange={(e) =>
                    setRegisterData({ ...registerData, firstName: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Last Name
                </label>
                <input
                  type="text"
                  value={registerData.lastName}
                  onChange={(e) =>
                    setRegisterData({ ...registerData, lastName: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={registerData.email}
                  onChange={(e) =>
                    setRegisterData({ ...registerData, email: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={registerData.username}
                  onChange={(e) =>
                    setRegisterData({ ...registerData, username: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  value={registerData.password}
                  onChange={(e) =>
                    setRegisterData({ ...registerData, password: e.target.value })
                  }
                  className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>

              <button
                type="submit"
                className="w-full px-4 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition-colors mt-6"
              >
                Create Account
              </button>
            </form>

            <button
              onClick={() => setView("splash")}
              className="w-full mt-4 px-4 py-2 text-slate-600 font-medium hover:text-slate-900 transition-colors"
            >
              Back
            </button>
          </div>
        </motion.div>
      )}
    </main>
  );
}
