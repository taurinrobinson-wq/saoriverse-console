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
  const [loginError, setLoginError] = useState("");
  const [registerError, setRegisterError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

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
    setLoginError("");
    setIsLoading(true);
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
        if (data.access_token) {
          localStorage.setItem("authToken", data.access_token);
        }
        window.location.href = "/chat";
      } else {
        setLoginError(data.error || "Login failed");
      }
    } catch (error) {
      console.error("Login failed:", error);
      setLoginError("Connection error. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setRegisterError("");
    setIsLoading(true);
    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(registerData),
      });
      const data = await response.json();
      if (response.ok && data.success) {
        setView("login");
        setRegisterError("");
        alert("Registration successful! Please log in.");
      } else {
        setRegisterError(data.error || "Registration failed");
      }
    } catch (error) {
      console.error("Registration failed:", error);
      setRegisterError("Connection error. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemo = async () => {
    try {
      window.location.href = "/chat?demo=true";
    } catch (error) {
      console.error("Demo load failed:", error);
    }
  };

  return (
    <main className="auth-container">
      {/* SPLASH SCREEN */}
      {view === "splash" && (
        <div className="splash-content">
          {/* Logo - stays visible */}
          <motion.div
            animate={
              logoMoving
                ? {
                    opacity: [1, 0, 1],
                  }
                : { opacity: 1 }
            }
            transition={{ duration: 0.8, ease: "easeInOut" }}
            className="splash-logo"
          >
            <Image
              src="/graphics/FirstPerson-Logo_cropped.svg"
              alt="FirstPerson Logo"
              fill
              className="object-contain"
              priority
            />
          </motion.div>

          {/* Text that appears after logo dissolve */}
          {logoMoving && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="splash-text"
            >
              <h1 className="splash-title">Personal Chat Companion</h1>

              {/* Buttons - Login/Register side by side, Demo below */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.4 }}
                className="splash-buttons"
              >
                <div className="splash-buttons-row">
                  <button
                    onClick={() => setView("login")}
                    className="btn btn-splash"
                  >
                    Login
                  </button>
                  <button
                    onClick={() => setView("register")}
                    className="btn btn-splash"
                  >
                    Register
                  </button>
                </div>
                <button
                  onClick={handleDemo}
                  className="btn btn-splash btn-splash-full"
                >
                  Demo
                </button>
              </motion.div>
            </motion.div>
          )}
        </div>
      )}

      {/* LOGIN FORM */}
      {view === "login" && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          className="auth-card"
        >
          <div className="auth-header">
            <h2 className="auth-title">Sign In</h2>
          </div>
          <form onSubmit={handleLogin} className="auth-form">
            {loginError && (
              <div className="form-error">{loginError}</div>
            )}
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                placeholder="Enter your username"
                value={loginUsername}
                onChange={(e) => setLoginUsername(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                required
              />
            </div>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isLoading}
            >
              {isLoading ? "Signing in..." : "Sign In"}
            </button>
            <button
              type="button"
              onClick={() => {
                setView("splash");
                setLoginError("");
              }}
              className="btn"
            >
              Back
            </button>
          </form>
        </motion.div>
      )}

      {/* REGISTER FORM */}
      {view === "register" && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          className="auth-card"
        >
          <div className="auth-header">
            <h2 className="auth-title">Create Account</h2>
          </div>
          <form onSubmit={handleRegister} className="auth-form">
            {registerError && (
              <div className="form-error">{registerError}</div>
            )}
            <div className="form-group">
              <label htmlFor="firstName">First Name</label>
              <input
                id="firstName"
                type="text"
                placeholder="First name"
                value={registerData.firstName}
                onChange={(e) =>
                  setRegisterData({ ...registerData, firstName: e.target.value })
                }
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="lastName">Last Name</label>
              <input
                id="lastName"
                type="text"
                placeholder="Last name"
                value={registerData.lastName}
                onChange={(e) =>
                  setRegisterData({ ...registerData, lastName: e.target.value })
                }
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                placeholder="your@email.com"
                value={registerData.email}
                onChange={(e) =>
                  setRegisterData({ ...registerData, email: e.target.value })
                }
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="reg-username">Username</label>
              <input
                id="reg-username"
                type="text"
                placeholder="Choose a username"
                value={registerData.username}
                onChange={(e) =>
                  setRegisterData({ ...registerData, username: e.target.value })
                }
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="reg-password">Password</label>
              <input
                id="reg-password"
                type="password"
                placeholder="Choose a password"
                value={registerData.password}
                onChange={(e) =>
                  setRegisterData({ ...registerData, password: e.target.value })
                }
                required
              />
            </div>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isLoading}
            >
              {isLoading ? "Creating..." : "Create Account"}
            </button>
            <button
              type="button"
              onClick={() => {
                setView("splash");
                setRegisterError("");
              }}
              className="btn"
            >
              Back
            </button>
          </form>
        </motion.div>
      )}
    </main>
  );
}
