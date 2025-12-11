"use client";

import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="text-center space-y-8 max-w-2xl px-4">
        <div className="space-y-4">
          <h1 className="text-5xl font-bold text-slate-900">FirstPerson</h1>
          <p className="text-xl text-slate-600">
            Talk with an emotionally aware AI companion
          </p>
        </div>

        <div className="flex gap-4 justify-center flex-wrap">
          <Link
            href="/chat"
            className="px-8 py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 transition"
          >
            🎤 Start Conversation
          </Link>
          <Link
            href="/settings"
            className="px-8 py-3 bg-slate-200 text-slate-900 rounded-lg font-semibold hover:bg-slate-300 transition"
          >
            ⚙️ Settings
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-12">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="text-3xl mb-2">🎙️</div>
            <h3 className="font-semibold mb-2">Voice First</h3>
            <p className="text-sm text-slate-600">
              Speak naturally. Real-time transcription and responses.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="text-3xl mb-2">❤️</div>
            <h3 className="font-semibold mb-2">Emotionally Aware</h3>
            <p className="text-sm text-slate-600">
              Understands emotions and responds with appropriate tone.
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="text-3xl mb-2">🏠</div>
            <h3 className="font-semibold mb-2">Fully Local</h3>
            <p className="text-sm text-slate-600">
              Runs locally. Your data stays with you.
            </p>
          </div>
        </div>
      </div>
    </main>
  );
}
