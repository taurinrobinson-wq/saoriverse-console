"use client";

import { motion } from "framer-motion";

export function DanceAnimation() {
  const celebrationEmojis = ["🎉", "🎊", "✨", "🌟", "💫", "🚀", "🎈"];

  return (
    <motion.div
      className="fixed inset-0 pointer-events-none flex items-center justify-center z-50"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      {/* Confetti-like elements */}
      {[...Array(12)].map((_, i) => (
        <motion.div
          key={i}
          className="absolute text-3xl"
          initial={{
            x: 0,
            y: 0,
            opacity: 1,
            rotate: 0,
          }}
          animate={{
            x: Math.cos((i / 12) * Math.PI * 2) * 200,
            y: Math.sin((i / 12) * Math.PI * 2) * 200 - 100,
            opacity: 0,
            rotate: 360 + Math.random() * 360,
          }}
          transition={{
            duration: 2,
            ease: "easeOut",
          }}
        >
          {celebrationEmojis[Math.floor(Math.random() * celebrationEmojis.length)]}
        </motion.div>
      ))}

      {/* Central burst animation */}
      <motion.div
        className="absolute w-32 h-32"
        initial={{ scale: 0, opacity: 1 }}
        animate={{ scale: 2, opacity: 0 }}
        transition={{ duration: 1.5, ease: "easeOut" }}
      >
        <div className="w-full h-full rounded-full bg-gradient-to-r from-yellow-400 via-pink-400 to-purple-400 blur-2xl" />
      </motion.div>

      {/* Floating hearts */}
      {[...Array(8)].map((_, i) => (
        <motion.div
          key={`heart-${i}`}
          className="absolute text-2xl"
          initial={{
            x: 0,
            y: 0,
            opacity: 1,
            scale: 1,
          }}
          animate={{
            x: (Math.random() - 0.5) * 300,
            y: (Math.random() - 0.5) * 300 - 150,
            opacity: 0,
            scale: 0,
          }}
          transition={{
            duration: 2.5,
            delay: i * 0.1,
            ease: "easeOut",
          }}
        >
          ❤️
        </motion.div>
      ))}

      {/* Pulsing rings */}
      {[1, 2, 3].map((ring) => (
        <motion.div
          key={`ring-${ring}`}
          className="absolute rounded-full border-2 border-indigo-400"
          style={{
            width: ring * 60,
            height: ring * 60,
            left: "50%",
            top: "50%",
            x: "-50%",
            y: "-50%",
          }}
          initial={{ scale: 0, opacity: 1 }}
          animate={{ scale: 3, opacity: 0 }}
          transition={{
            duration: 1.2,
            delay: ring * 0.1,
            ease: "easeOut",
          }}
        />
      ))}

      {/* Celebration text */}
      <motion.div
        className="absolute text-center space-y-2"
        initial={{ opacity: 0, scale: 0.5 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.2 }}
      >
        <motion.h2
          className="text-4xl font-bold bg-gradient-to-r from-yellow-400 via-pink-400 to-purple-400 bg-clip-text text-transparent"
          animate={{
            y: [0, -20, 0],
            scale: [1, 1.1, 1],
          }}
          transition={{
            duration: 0.8,
            repeat: 2,
          }}
        >
          That's Amazing! 🎉
        </motion.h2>
      </motion.div>
    </motion.div>
  );
}
