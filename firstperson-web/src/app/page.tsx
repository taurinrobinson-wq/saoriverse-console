"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowRight, Mic, Brain, Lock } from "lucide-react";

export default function Home() {
  const [showContent, setShowContent] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setShowContent(true), 300);
    return () => clearTimeout(timer);
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.3,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: { duration: 0.8, ease: "easeOut" },
    },
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900 text-white overflow-hidden">
      <motion.div
        className="absolute top-0 left-0 w-96 h-96 bg-indigo-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
        animate={{
          x: [0, 50, -50, 0],
          y: [0, -50, 50, 0],
        }}
        transition={{ duration: 20, repeat: Infinity }}
      />
      <motion.div
        className="absolute bottom-0 right-0 w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20"
        animate={{
          x: [0, -50, 50, 0],
          y: [0, 50, -50, 0],
        }}
        transition={{ duration: 25, repeat: Infinity }}
      />

      <motion.div
        className="container mx-auto px-4 py-12 relative z-10"
        variants={containerVariants}
        initial="hidden"
        animate={showContent ? "visible" : "hidden"}
      >
        <motion.div className="text-center mb-16" variants={itemVariants}>
          <motion.div
            className="inline-block mb-6"
            animate={{ y: [0, -10, 0] }}
            transition={{ duration: 3, repeat: Infinity }}
          >
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-indigo-600 to-blue-600 flex items-center justify-center text-4xl shadow-2xl">
              🧠
            </div>
          </motion.div>

          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-indigo-400 to-blue-400 bg-clip-text text-transparent">
            FirstPerson
          </h1>
          <p className="text-2xl text-indigo-200 mb-4">
            Talk with an emotionally aware AI companion
          </p>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto">
            Experience conversations that understand emotion, respond with personality, and evolve with you.
          </p>
        </motion.div>

        <motion.div
          className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16"
          variants={containerVariants}
        >
          {[
            {
              icon: Mic,
              title: "Voice First",
              description:
                "Record your message and get audio responses with emotional understanding.",
            },
            {
              icon: Brain,
              title: "Smart Responses",
              description:
                "Powered by local LLM with emotional intelligence analysis.",
            },
            {
              icon: Lock,
              title: "100% Private",
              description: "All processing happens locally. Your data stays with you.",
            },
          ].map((feature, index) => (
            <motion.div
              key={index}
              variants={itemVariants}
              className="group relative bg-gradient-to-br from-slate-800 to-slate-900 p-8 rounded-xl border border-slate-700 hover:border-indigo-500 transition-all duration-300 overflow-hidden"
            >
              <motion.div
                className="absolute inset-0 bg-gradient-to-br from-indigo-600/10 to-blue-600/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                whileHover={{ opacity: 1 }}
              />

              <div className="relative z-10">
                <motion.div
                  className="inline-block mb-4 p-3 bg-gradient-to-br from-indigo-600 to-blue-600 rounded-lg"
                  whileHover={{ scale: 1.1, rotate: 5 }}
                >
                  <feature.icon className="w-6 h-6 text-white" />
                </motion.div>

                <h2 className="text-2xl font-bold mb-3">{feature.title}</h2>
                <p className="text-slate-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </motion.div>
          ))}
        </motion.div>

        <motion.div variants={itemVariants} className="mb-16">
          <h3 className="text-3xl font-bold text-center mb-8">
            Experience the magic
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              "Emotional awareness",
              "Dance mode",
              "Memory & context",
              "Multi-model support",
              "Real-time transcription",
              "Voice synthesis",
              "Glyph visualization",
              "Settings & preferences",
            ].map((capability, index) => (
              <motion.div
                key={index}
                className="flex items-center justify-center p-4 bg-slate-800/50 rounded-lg border border-slate-700 hover:border-indigo-500 transition-all"
                whileHover={{ scale: 1.05, y: -5 }}
              >
                <span className="text-sm font-medium text-indigo-300">
                  ✨ {capability}
                </span>
              </motion.div>
            ))}
          </div>
        </motion.div>

        <motion.div variants={itemVariants} className="text-center">
          <Link href="/chat">
            <motion.button
              className="px-8 py-4 bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 rounded-lg font-bold text-lg transition-all shadow-lg hover:shadow-2xl inline-flex items-center gap-2 group"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              Start Chatting
              <motion.span
                animate={{ x: [0, 5, 0] }}
                transition={{ duration: 1.5, repeat: Infinity }}
              >
                <ArrowRight className="w-5 h-5" />
              </motion.span>
            </motion.button>
          </Link>
        </motion.div>

        {[...Array(5)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-indigo-400 rounded-full opacity-50"
            animate={{
              x: Math.cos(i) * 200,
              y: Math.sin(i) * 200,
              opacity: [0.3, 0.7, 0.3],
            }}
            transition={{
              duration: 4 + i,
              repeat: Infinity,
              ease: "linear",
            }}
            style={{
              left: `${20 + i * 15}%`,
              top: `${30 + i * 10}%`,
            }}
          />
        ))}
      </motion.div>
    </main>
  );
}
