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
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username: loginUsername,
          password: loginPassword,
        }),
      });
      const data = await response.json();
      if (response.ok && data.success) {
        // Store token if provided
        if (data.access_token) {
          localStorage.setItem("authToken", data.access_token);
        }
        window.location.href = "/chat";
      } else {
        alert(data.error || "Login failed");
      }
    } catch (error) {
      console.error("Login failed:", error);
      alert("Login error");
    }
  };

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(registerData),
      });
      const data = await response.json();
      if (response.ok && data.success) {
        setView("login");
        alert("Registration successful! Please log in.");
      } else {
        alert(data.error || "Registration failed");
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
    <main style={{ width: '100vw', height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'white' }}>
      {view === "splash" && (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '48px' }}>
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
            className="relative w-24 h-24"
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
                className="flex flex-col gap-8 w-72"
              >
                <button
                  onClick={() => setView("login")}
                  className="px-8 py-4 bg-white text-slate-900 border border-slate-300 rounded font-medium hover:bg-slate-50 transition-colors text-base"
                >
                  Login
                </button>
                <button
                  onClick={() => setView("register")}
                  className="px-8 py-4 bg-white text-slate-900 border border-slate-300 rounded font-medium hover:bg-slate-50 transition-colors text-base"
                >
                  Register
                </button>
                <button
                  onClick={handleDemo}
                  className="px-8 py-4 bg-white text-slate-900 border border-slate-300 rounded font-medium hover:bg-slate-50 transition-colors text-base"
                >
                  Demo
                </button>
              </motion.div>
            </motion.div>
          )}
        </div>
      )}

      {view === "login" && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          style={{ width: '100vw', height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'white' }}
        >
          <div style={{ backgroundColor: 'white', padding: '32px', width: '100%', maxWidth: '400px' }}>
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
          style={{ width: '100vw', height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'white' }}
        >
          <div style={{ backgroundColor: 'white', padding: '32px', width: '100%', maxWidth: '400px' }}>
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
