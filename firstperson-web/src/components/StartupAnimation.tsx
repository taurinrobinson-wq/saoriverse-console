"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useRouter } from "next/navigation";

export default function StartupAnimation() {
  const [isComplete, setIsComplete] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Auto-navigate after animation completes (5 seconds)
    const timer = setTimeout(() => {
      setIsComplete(true);
      setTimeout(() => {
        router.push("/chat");
      }, 1000);
    }, 5000);

    return () => clearTimeout(timer);
  }, [router]);

  return (
    <motion.div
      className="w-full h-screen flex flex-col items-center justify-center overflow-hidden bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900"
      initial={{ opacity: 1 }}
      animate={{ opacity: isComplete ? 0 : 1 }}
      transition={{ duration: 1, delay: 4 }}
    >
      {/* Animated background orbs */}
      <motion.div
        className="absolute top-20 left-20 w-72 h-72 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
        animate={{
          x: [0, 20, -20, 0],
          y: [0, -30, 30, 0],
        }}
        transition={{ duration: 8, repeat: Infinity }}
      />
      <motion.div
        className="absolute bottom-20 right-20 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
        animate={{
          x: [0, -20, 20, 0],
          y: [0, 30, -30, 0],
        }}
        transition={{ duration: 10, repeat: Infinity }}
      />
      <motion.div
        className="absolute top-1/2 left-1/3 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
        animate={{
          x: [0, 30, -30, 0],
          y: [0, 20, -20, 0],
        }}
        transition={{ duration: 12, repeat: Infinity }}
      />

      {/* Logo container */}
      <motion.div
        className="relative z-10 flex flex-col items-center gap-8"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        {/* Logo circle background */}
        <motion.div
          className="w-40 h-40 rounded-full bg-gradient-to-br from-indigo-600 to-blue-600 flex items-center justify-center shadow-2xl"
          animate={{
            boxShadow: [
              "0 0 20px rgba(99, 102, 241, 0.3)",
              "0 0 40px rgba(99, 102, 241, 0.6)",
              "0 0 20px rgba(99, 102, 241, 0.3)",
            ],
          }}
          transition={{ duration: 2, repeat: Infinity }}
        >
          {/* Logo text - brain emoji as placeholder */}
          <motion.div
            className="text-7xl"
            animate={{
              y: [0, -5, 0],
            }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            🧠
          </motion.div>
        </motion.div>

        {/* Title */}
        <motion.h1
          className="text-5xl font-bold text-white text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          FirstPerson
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          className="text-xl text-indigo-200 text-center max-w-md"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          Talk with an emotionally aware AI companion
        </motion.p>

        {/* Animated loading indicator */}
        <motion.div className="flex gap-2 mt-8">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              className="w-3 h-3 bg-indigo-400 rounded-full"
              animate={{
                opacity: [0.3, 1, 0.3],
                scale: [1, 1.2, 1],
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                delay: i * 0.2,
              }}
            />
          ))}
        </motion.div>
      </motion.div>

      {/* Dissolving effect - reveals chat */}
      {isComplete && (
        <motion.div
          className="absolute inset-0 bg-slate-900"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1 }}
        />
      )}
    </motion.div>
  );
}
