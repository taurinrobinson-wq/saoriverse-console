"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Image from "next/image";

type View = "splash" | "login" | "register";

export default function Home() {
  const [view, setView] = useState<View>("splash");
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
    if (view === "splash") {
      const timer = setTimeout(() => {
        setLogoMoving(true);
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [view]);

  const handleLogin = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const response = await fetch("/api/auth", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: loginUsername,
          password: loginPassword,
        }),
      });
      if (response.ok) {
        window.location.href = "/chat";
      } else {
        alert("Login failed");
      }
    } catch (error) {
      console.error("Login failed:", error);
      alert("Login error");
    }
  };

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const response = await fetch("/api/auth-manager", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(registerData),
      });
      if (response.ok) {
        setView("login");
        alert("Registration successful! Please log in.");
      } else {
        alert("Registration failed");
      }
    } catch (error) {
      console.error("Registration failed:", error);
      alert("Registration error");
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
    <main className="min-h-screen bg-white flex items-center justify-center p-4">
      {view === "splash" && (
        <motion.div className="flex flex-col items-center justify-center gap-12 max-w-md">
          {/* Logo - smaller and centered */}
          <motion.div
            animate={
              logoMoving
                ? {
                    opacity: 0,
                    scale: 0.5,
                    y: -100,
                  }
                : { opacity: 1, scale: 1, y: 0 }
            }
            transition={{ duration: 1.2, ease: "easeInOut" }}
            className="relative w-32 h-32"
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
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="text-center"
            >
              <h1 className="text-2xl font-light text-slate-900 mb-8">
                Personal Companion
              </h1>

              {/* Buttons - white with black text, cleaner style */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
                className="flex flex-col gap-3 w-full"
              >
                <button
                  onClick={() => setView("login")}
                  className="px-6 py-2.5 bg-white text-slate-900 border border-slate-300 rounded font-medium hover:bg-slate-50 transition-colors"
                >
                  Login
                </button>
                <button
                  onClick={() => setView("register")}
                  className="px-6 py-2.5 bg-white text-slate-900 border border-slate-300 rounded font-medium hover:bg-slate-50 transition-colors"
                >
                  Register
                </button>
                <button
                  onClick={handleDemo}
                  className="px-6 py-2.5 bg-white text-slate-900 border border-slate-300 rounded font-medium hover:bg-slate-50 transition-colors"
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
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          className="w-full max-w-sm"
        >
          <div className="bg-white p-8">
            <h2 className="text-xl font-light text-slate-900 mb-6 text-center">
              Login
            </h2>

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <input
                  type="text"
                  placeholder="Username"
                  value={loginUsername}
                  onChange={(e) => setLoginUsername(e.target.value)}
                  className="w-full px-4 py-2 border border-slate-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-slate-400"
                  required
                />
              </div>

              <div>
                <input
                  type="password"
                  placeholder="Password"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  className="w-full px-4 py-2 border border-slate-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-slate-400"
                  required
                />
              </div>

              <button
                type="submit"
                className="w-full px-4 py-2 bg-white text-slate-900 border border-slate-300 rounded font-medium hover:bg-slate-50 transition-colors mt-6"
              >
                Sign In
              </button>
            </form>

            <button
              onClick={() => setView("splash")}
              className="w-full mt-4 px-4 py-2 text-slate-500 text-sm font-medium hover:text-slate-700 transition-colors"
            >
              Back
            </button>
          </div>
        </motion.div>
      )}

      {view === "register" && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          className="w-full max-w-sm"
        >
          <div className="bg-white p-8">
            <h2 className="text-xl font-light text-slate-900 mb-6 text-center">
              Register
            </h2>

            <form onSubmit={handleRegister} className="space-y-3">
              <input
                type="text"
                placeholder="First Name"
                value={registerData.firstName}
                onChange={(e) =>
                  setRegisterData({ ...registerData, firstName: e.target.value })
                }
                className="w-full px-4 py-2 border border-slate-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-slate-400"
                required
              />

              <input
                type="text"
                placeholder="Last Name"
                value={registerData.lastName}
                onChange={(e) =>
                  setRegisterData({ ...registerData, lastName: e.target.value })
                }
                className="w-full px-4 py-2 border border-slate-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-slate-400"
                required
              />

              <input
                type="email"
                placeholder="Email"
                value={registerData.email}
                onChange={(e) =>
                  setRegisterData({ ...registerData, email: e.target.value })
                }
                className="w-full px-4 py-2 border border-slate-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-slate-400"
                required
              />

              <input
                type="text"
                placeholder="Username"
                value={registerData.username}
                onChange={(e) =>
                  setRegisterData({ ...registerData, username: e.target.value })
                }
                className="w-full px-4 py-2 border border-slate-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-slate-400"
                required
              />

              <input
                type="password"
                placeholder="Password"
                value={registerData.password}
                onChange={(e) =>
                  setRegisterData({ ...registerData, password: e.target.value })
                }
                className="w-full px-4 py-2 border border-slate-300 rounded text-sm focus:outline-none focus:ring-1 focus:ring-slate-400"
                required
              />

              <button
                type="submit"
                className="w-full px-4 py-2 bg-white text-slate-900 border border-slate-300 rounded font-medium hover:bg-slate-50 transition-colors mt-4"
              >
                Create Account
              </button>
            </form>

            <button
              onClick={() => setView("splash")}
              className="w-full mt-4 px-4 py-2 text-slate-500 text-sm font-medium hover:text-slate-700 transition-colors"
            >
              Back
            </button>
          </div>
        </motion.div>
      )}
    </main>
  );
}
