"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
};

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem("authToken");
    if (!token) {
      router.push("/");
      return;
    }
    // TODO: Decode token to get user info
    setUser({ username: "User" });
  }, [router]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      // Call our Next.js API which proxies to the Python backend
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage.content,
          userId: user?.user_id || "demo_user",
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: data.message || "I'm listening...",
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
      } else {
        throw new Error(data.error || "Failed to get response");
      }
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    router.push("/");
  };

  if (!user) return null;

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-title">FirstPerson - Personal Companion</div>
        <button onClick={handleLogout} className="btn">
          Logout
        </button>
      </div>

      {/* Main Chat Area */}
      <div className="chat-main">
        {/* Sidebar */}
        <div className="chat-sidebar">
          <h3 style={{ marginBottom: "1rem", color: "var(--text-primary)" }}>
            Conversations
          </h3>
          <div
            style={{
              color: "var(--text-secondary)",
              fontSize: "0.875rem",
            }}
          >
            New conversation
          </div>
        </div>

        {/* Messages */}
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div
              style={{
                textAlign: "center",
                color: "var(--text-secondary)",
                marginTop: "2rem",
              }}
            >
              <p>Start a conversation by typing below...</p>
            </div>
          ) : (
            messages.map((msg) => (
              <div key={msg.id} className={`message ${msg.role}`}>
                <div className="message-content">{msg.content}</div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="message assistant">
              <div className="message-content">
                <div style={{ display: "flex", gap: "0.25rem" }}>
                  <span
                    style={{
                      animation: "pulse 1.4s infinite",
                      width: "0.5rem",
                      height: "0.5rem",
                      borderRadius: "50%",
                      background: "var(--text-secondary)",
                    }}
                  />
                  <span
                    style={{
                      animation: "pulse 1.4s infinite 0.2s",
                      width: "0.5rem",
                      height: "0.5rem",
                      borderRadius: "50%",
                      background: "var(--text-secondary)",
                    }}
                  />
                  <span
                    style={{
                      animation: "pulse 1.4s infinite 0.4s",
                      width: "0.5rem",
                      height: "0.5rem",
                      borderRadius: "50%",
                      background: "var(--text-secondary)",
                    }}
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Chat Input */}
      <form onSubmit={handleSendMessage} className="chat-input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Share what you're feeling..."
          disabled={isLoading}
        />
        <button type="submit" className="btn btn-primary" disabled={isLoading}>
          {isLoading ? "..." : "Send"}
        </button>
      </form>

      <style jsx>{`
        @keyframes pulse {
          0%,
          60%,
          100% {
            opacity: 0.3;
          }
          30% {
            opacity: 1;
          }
        }
      `}</style>
    </div>
  );
}
