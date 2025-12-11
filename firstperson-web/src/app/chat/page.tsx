"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useStore } from "@/lib/store";
import { api } from "@/lib/api";
import { AudioRecorder } from "@/components/AudioRecorder";
import { ResponseDisplay } from "@/components/ResponseDisplay";
import { DanceAnimation } from "@/components/DanceAnimation";
import { Settings, Send } from "lucide-react";
import Link from "next/link";

interface Message {
  id: string;
  type: "user" | "assistant";
  text: string;
  glyphIntent?: string;
  audioUrl?: string;
  timestamp: Date;
  emotion?: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showDance, setShowDance] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { recordingStatus, selectedModel } = useStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      text: text,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText("");
    setIsLoading(true);

    try {
      const response = await api.chat(text);

      const shouldDance = detectExcitement(response.response_text);
      if (shouldDance) {
        setShowDance(true);
        setTimeout(() => setShowDance(false), 3000);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        text: response.response_text,
        glyphIntent: response.glyph_intent,
        emotion: response.emotion,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (response.glyph_intent) {
        try {
          const audioUrl = await api.synthesize(
            response.response_text,
            response.glyph_intent
          );
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessage.id ? { ...msg, audioUrl } : msg
            )
          );
        } catch (error) {
          console.error("Audio synthesis failed:", error);
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          type: "assistant",
          text: "Sorry, something went wrong. Please try again.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const detectExcitement = (text: string): boolean => {
    const excitementPatterns = [
      /amazing/i,
      /awesome/i,
      /wonderful/i,
      /exciting/i,
      /fantastic/i,
      /love/i,
      /beautiful/i,
      /🎉|🎊|✨|🌟|💫/,
    ];
    return excitementPatterns.some((pattern) => pattern.test(text));
  };

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-900 via-indigo-900 to-slate-900">
      <motion.div
        className="bg-slate-800/80 backdrop-blur-md border-b border-slate-700 px-6 py-4 flex items-center justify-between"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <motion.div
          className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-blue-400 bg-clip-text text-transparent flex items-center gap-3"
          whileHover={{ scale: 1.05 }}
        >
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-600 to-blue-600 flex items-center justify-center text-xl">
            🧠
          </div>
          FirstPerson Chat
        </motion.div>

        <div className="flex items-center gap-4">
          <motion.span
            className="text-sm text-indigo-300 px-3 py-1 bg-slate-700 rounded-full"
            animate={{ opacity: [0.7, 1, 0.7] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            {selectedModel || "Local AI"}
          </motion.span>

          <Link href="/settings">
            <motion.button
              className="p-2 hover:bg-slate-700 rounded-lg transition-colors"
              whileHover={{ scale: 1.1, rotate: 90 }}
              whileTap={{ scale: 0.95 }}
            >
              <Settings className="w-5 h-5 text-indigo-300" />
            </motion.button>
          </Link>
        </div>
      </motion.div>

      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4 custom-scrollbar">
        <AnimatePresence>
          {messages.length === 0 && (
            <motion.div
              className="flex items-center justify-center h-full"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="text-center space-y-4">
                <motion.div
                  className="text-6xl"
                  animate={{ y: [0, -20, 0] }}
                  transition={{ duration: 3, repeat: Infinity }}
                >
                  🎤
                </motion.div>
                <p className="text-xl text-slate-400">
                  Start your conversation by speaking or typing
                </p>
              </div>
            </motion.div>
          )}

          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
              className={`flex ${
                message.type === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <motion.div
                className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                  message.type === "user"
                    ? "bg-gradient-to-br from-indigo-600 to-blue-600 text-white"
                    : "bg-slate-800 text-slate-100 border border-slate-700"
                }`}
                whileHover={{ scale: 1.02 }}
                transition={{ duration: 0.2 }}
              >
                <p className="text-sm leading-relaxed">{message.text}</p>

                {message.type === "assistant" && (
                  <div className="mt-2 flex items-center gap-2 text-xs text-slate-400">
                    {message.emotion && (
                      <span className="px-2 py-1 bg-slate-700 rounded-full">
                        {message.emotion}
                      </span>
                    )}
                    {message.audioUrl && (
                      <motion.button
                        className="px-2 py-1 bg-indigo-600 rounded-full text-indigo-100 hover:bg-indigo-700"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => {
                          const audio = new Audio(message.audioUrl);
                          audio.play();
                        }}
                      >
                        🔊 Play
                      </motion.button>
                    )}
                  </div>
                )}
              </motion.div>
            </motion.div>
          ))}

          {isLoading && (
            <motion.div
              className="flex justify-start"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <div className="flex gap-2 px-4 py-3 bg-slate-800 rounded-2xl border border-slate-700">
                {[0, 1, 2].map((i) => (
                  <motion.div
                    key={i}
                    className="w-2 h-2 bg-indigo-400 rounded-full"
                    animate={{
                      y: [0, -10, 0],
                    }}
                    transition={{
                      duration: 0.6,
                      repeat: Infinity,
                      delay: i * 0.1,
                    }}
                  />
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </div>

      <AnimatePresence>
        {showDance && <DanceAnimation />}
      </AnimatePresence>

      <motion.div
        className="bg-slate-800/80 backdrop-blur-md border-t border-slate-700 px-6 py-4 space-y-4"
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
      >
        <div className="flex gap-3">
          <motion.input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage(inputText);
              }
            }}
            placeholder="Type a message or use voice..."
            className="flex-1 bg-slate-700 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:border-indigo-500 transition-colors"
            whileFocus={{ scale: 1.02 }}
          />

          <motion.button
            onClick={() => handleSendMessage(inputText)}
            disabled={!inputText.trim() || isLoading}
            className="px-4 py-3 bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-white font-medium transition-all"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Send className="w-5 h-5" />
          </motion.button>
        </div>

        <AudioRecorder
          onTranscription={(text) => handleSendMessage(text)}
          isLoading={isLoading}
        />
      </motion.div>

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(99, 102, 241, 0.3);
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(99, 102, 241, 0.5);
        }
      `}</style>
    </div>
  );
}
