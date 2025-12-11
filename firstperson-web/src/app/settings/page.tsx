"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { useAudioStore } from "@/lib/store";
import Link from "next/link";
import { ArrowLeft, ToggleRight, ToggleLeft } from "lucide-react";

export default function SettingsPage() {
  const {
    selectedModel,
    danceModeEnabled,
    voiceSettings,
    setSelectedModel,
    setDanceModeEnabled,
    setVoiceSettings,
  } = useAudioStore();

  const [isSaved, setIsSaved] = useState(false);

  const handleSave = () => {
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 2000);
  };

  const models = ["orca-mini", "llama2", "mistral", "neural-chat"];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900 text-white">
      {/* Header */}
      <motion.div
        className="bg-slate-800/80 backdrop-blur-md border-b border-slate-700 px-6 py-4 flex items-center gap-4"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Link href="/chat">
          <motion.button
            className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
          >
            <ArrowLeft className="w-5 h-5 text-indigo-300" />
          </motion.button>
        </Link>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-400 to-blue-400 bg-clip-text text-transparent">
          Settings
        </h1>
      </motion.div>

      {/* Settings Container */}
      <div className="max-w-2xl mx-auto px-6 py-8 space-y-6">
        {/* Model Selection */}
        <motion.div
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          whileHover={{ borderColor: "#818cf8" }}
        >
          <h2 className="text-xl font-bold mb-4">AI Model</h2>
          <p className="text-slate-400 mb-4">Select which LLM model to use:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {models.map((model) => (
              <motion.button
                key={model}
                onClick={() => setSelectedModel(model)}
                className={`p-3 rounded-lg font-medium transition-all ${
                  selectedModel === model
                    ? "bg-gradient-to-r from-indigo-600 to-blue-600 text-white"
                    : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {model}
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Dance Mode */}
        <motion.div
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          whileHover={{ borderColor: "#818cf8" }}
        >
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-bold">Dance Mode</h2>
              <p className="text-slate-400 text-sm mt-1">
                Play animations when discussing exciting topics
              </p>
            </div>
            <motion.button
              onClick={() => {
                setDanceModeEnabled(!danceModeEnabled);
                handleSave();
              }}
              className="text-indigo-400 hover:text-indigo-300 transition-colors"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              {danceModeEnabled ? (
                <ToggleRight className="w-8 h-8" />
              ) : (
                <ToggleLeft className="w-8 h-8" />
              )}
            </motion.button>
          </div>

          {danceModeEnabled && (
            <motion.div
              className="bg-indigo-900/30 border border-indigo-700 rounded-lg p-4"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
            >
              <p className="text-indigo-200 text-sm">
                ✨ Dance mode is enabled! The AI will perform celebratory animations during exciting conversations.
              </p>
            </motion.div>
          )}
        </motion.div>

        {/* Voice Settings */}
        <motion.div
          className="bg-slate-800/50 border border-slate-700 rounded-xl p-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          whileHover={{ borderColor: "#818cf8" }}
        >
          <h2 className="text-xl font-bold mb-6">Voice Settings</h2>

          <div className="space-y-6">
            {/* Pitch */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-medium">Pitch: {voiceSettings.pitch.toFixed(1)}x</label>
              </div>
              <motion.input
                type="range"
                min="0.5"
                max="2"
                step="0.1"
                value={voiceSettings.pitch}
                onChange={(e) =>
                  setVoiceSettings({ pitch: parseFloat(e.target.value) })
                }
                className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                whileHover={{ scale: 1.02 }}
              />
            </div>

            {/* Rate */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-medium">Speech Rate: {voiceSettings.rate} WPM</label>
              </div>
              <motion.input
                type="range"
                min="100"
                max="300"
                step="10"
                value={voiceSettings.rate}
                onChange={(e) =>
                  setVoiceSettings({ rate: parseInt(e.target.value) })
                }
                className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                whileHover={{ scale: 1.02 }}
              />
            </div>

            {/* Volume */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-medium">Volume: {(voiceSettings.volume * 100).toFixed(0)}%</label>
              </div>
              <motion.input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={voiceSettings.volume}
                onChange={(e) =>
                  setVoiceSettings({ volume: parseFloat(e.target.value) })
                }
                className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                whileHover={{ scale: 1.02 }}
              />
            </div>
          </div>
        </motion.div>

        {/* Save Indicator */}
        {isSaved && (
          <motion.div
            className="fixed bottom-8 right-8 bg-gradient-to-r from-green-600 to-emerald-600 px-6 py-3 rounded-lg text-white font-medium shadow-lg"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
          >
            ✓ Settings saved!
          </motion.div>
        )}
      </div>
    </div>
  );
}
