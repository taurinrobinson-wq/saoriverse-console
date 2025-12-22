"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import ResponseMetadata from "@/components/ResponseMetadata";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  glyph_voltage?: string;
  metadata?: {
    firstperson_orchestrator?: {
      mortality_salience?: number;
      memory_context_injected?: boolean;
      frequency_reflection?: string;
      safety_signal?: boolean;
      affect_analysis?: { valence?: number; intensity?: number };
    };
  };
};

type Conversation = {
  conversation_id: string;
  title: string;
  updated_at: string;
  message_count: number;
};

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [newTitle, setNewTitle] = useState("");

  // Audio state
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isSynthesizing, setIsSynthesizing] = useState(false);
  const [transcript, setTranscript] = useState("");
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem("authToken");
    if (!token) {
      router.push("/");
      return;
    }

    // Decode token to get user info
    const userInfo = localStorage.getItem("userInfo");
    if (userInfo) {
      const userData = JSON.parse(userInfo);
      setUser(userData);
      loadConversations(userData.username);
    } else {
      setUser({ username: "User" });
    }
  }, [router]);

  const loadConversations = async (userId: string) => {
    try {
      const response = await fetch(`/api/conversations?userId=${userId}`);
      const data = await response.json();
      if (data.success) {
        setConversations(data.conversations || []);
      }
    } catch (error) {
      console.error("Error loading conversations:", error);
    }
  };

  const loadConversation = async (conversationId: string) => {
    try {
      const response = await fetch(`/api/conversation/${user?.username}/${conversationId}`);
      const data = await response.json();

      if (data.success && data.message) {
        const conv = JSON.parse(data.message);
        // Convert messages to the format we use
        const loadedMessages: Message[] = (conv.messages || []).map((msg: any, idx: number) => ({
          id: idx.toString(),
          role: msg.role,
          content: msg.content,
          timestamp: new Date(),
        }));
        setMessages(loadedMessages);
        setCurrentConversationId(conversationId);
        setNewTitle(conv.title || "");
      }
    } catch (error) {
      console.error("Error loading conversation:", error);
    }
  };

  // Audio Functions
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: "audio/webm" });
        await transcribeAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error starting recording:", error);
      alert("Unable to access microphone. Please check permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const transcribeAudio = async (audioBlob: Blob) => {
    setIsTranscribing(true);
    try {
      const formData = new FormData();
      formData.append("file", audioBlob, "audio.webm");

      const response = await fetch("http://localhost:8000/transcribe", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (data.success && data.text) {
        setTranscript(data.text);
        setInput(data.text);
      }
    } catch (error) {
      console.error("Error transcribing:", error);
      alert("Transcription failed. Please try again.");
    } finally {
      setIsTranscribing(false);
    }
  };

  const playSynthesis = async (text: string) => {
    setIsSynthesizing(true);
    try {
      const response = await fetch("http://localhost:8000/synthesize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });

      const data = await response.json();
      if (data.success && data.audio_url) {
        if (audioRef.current) {
          audioRef.current.src = data.audio_url;
          audioRef.current.play();
        }
      }
    } catch (error) {
      console.error("Error synthesizing:", error);
    } finally {
      setIsSynthesizing(false);
    }
  };

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
      // Generate conversation ID if this is the first message
      const isFirstMessage = messages.length === 0;
      const conversationId = currentConversationId || Math.random().toString(36).substring(7);

      // Call our Next.js API which proxies to the Python backend
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage.content,
          userId: user?.username || "demo_user",
          context: {
            conversation_id: conversationId,
            is_first_message: isFirstMessage,
            messages: messages.map(m => ({ role: m.role, content: m.content })),
            title: newTitle || (isFirstMessage ? userMessage.content.substring(0, 50) : ""),
          },
        }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: data.message || "I'm listening...",
          timestamp: new Date(),
          glyph_voltage: data.glyph_voltage,
          metadata: data.metadata,
        };
        setMessages((prev) => [...prev, assistantMessage]);

        // Auto-synthesize response to audio
        if (data.message) {
          await playSynthesis(data.message);
        }

        // Update conversation ID from response
        if (data.conversation_id && !currentConversationId) {
          setCurrentConversationId(data.conversation_id);
        }

        // Reload conversations to show new one or updates
        if (user?.username) {
          loadConversations(user.username);
        }
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

  const handleDeleteConversation = async (conversationId: string) => {
    if (!confirm("Delete this conversation?")) return;

    try {
      const response = await fetch(`/api/conversation/${user?.username}/${conversationId}`, {
        method: "DELETE",
      });
      const data = await response.json();

      if (data.success) {
        setConversations((prev) => prev.filter((c) => c.conversation_id !== conversationId));
        if (currentConversationId === conversationId) {
          setCurrentConversationId(null);
          setMessages([]);
        }
      }
    } catch (error) {
      console.error("Error deleting conversation:", error);
    }
  };

  const handleRenameConversation = async (conversationId: string) => {
    try {
      const response = await fetch(`/api/conversation/${user?.username}/${conversationId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ new_title: newTitle }),
      });
      const data = await response.json();

      if (data.success) {
        setConversations((prev) =>
          prev.map((c) => (c.conversation_id === conversationId ? { ...c, title: newTitle } : c))
        );
        setIsEditingTitle(false);
      }
    } catch (error) {
      console.error("Error renaming conversation:", error);
    }
  };

  const handleFeedback = async (messageId: string, helpful: boolean) => {
    try {
      await fetch("/api/feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message_id: messageId,
          conversation_id: currentConversationId,
          helpful,
          user_id: user?.username || "demo_user",
        }),
      });
    } catch (error) {
      console.error("Error submitting feedback:", error);
    }
  };

  const handleNewConversation = () => {
    setCurrentConversationId(null);
    setMessages([]);
    setNewTitle("");
    setIsEditingTitle(false);
  };

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    localStorage.removeItem("userInfo");
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
          <button onClick={handleNewConversation} className="btn btn-sidebar-new">
            + New Conversation
          </button>

          <h3 style={{ marginBottom: "1rem", marginTop: "1rem", color: "var(--text-primary)" }}>
            Conversations
          </h3>

          <div className="conversations-list">
            {conversations.length === 0 ? (
              <div style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>
                No conversations yet
              </div>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.conversation_id}
                  className={`conversation-item ${currentConversationId === conv.conversation_id ? "active" : ""
                    }`}
                  onClick={() => loadConversation(conv.conversation_id)}
                >
                  <div className="conv-title">{conv.title}</div>
                  <div className="conv-meta">
                    {conv.message_count} messages
                  </div>
                  <div className="conv-actions">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setCurrentConversationId(conv.conversation_id);
                        setNewTitle(conv.title);
                        setIsEditingTitle(true);
                      }}
                      className="action-btn"
                      title="Edit"
                    >
                      ✎
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteConversation(conv.conversation_id);
                      }}
                      className="action-btn delete"
                      title="Delete"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Messages */}
        <div className="chat-messages">
          {messages.length === 0 && !currentConversationId ? (
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
                {msg.role === "assistant" && msg.metadata && (
                  <ResponseMetadata
                    metadata={msg.metadata}
                    messageId={msg.id}
                    onFeedback={handleFeedback}
                  />
                )}
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

        {/* Audio Controls */}
        <div className="audio-controls">
          {isRecording ? (
            <button
              type="button"
              onClick={stopRecording}
              className="btn btn-recording"
              title="Stop Recording"
            >
              ⏹ Stop
            </button>
          ) : (
            <button
              type="button"
              onClick={startRecording}
              disabled={isTranscribing || isLoading}
              className="btn btn-secondary"
              title="Start Recording"
            >
              🎤
            </button>
          )}

          {isTranscribing && <span className="status">Transcribing...</span>}
          {isSynthesizing && <span className="status">Speaking...</span>}
        </div>

        <button type="submit" className="btn btn-primary" disabled={isLoading || isRecording}>
          {isLoading ? "..." : "Send"}
        </button>

        <audio ref={audioRef} hidden />
      </form>

      {/* Rename Modal */}
      {isEditingTitle && currentConversationId && (
        <div className="modal-overlay" onClick={() => setIsEditingTitle(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h3>Rename Conversation</h3>
            <input
              type="text"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="New title"
              autoFocus
            />
            <div className="modal-buttons">
              <button
                onClick={() => handleRenameConversation(currentConversationId)}
                className="btn btn-primary"
              >
                Save
              </button>
              <button onClick={() => setIsEditingTitle(false)} className="btn">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

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

        .btn-sidebar-new {
          width: 100%;
          padding: 0.75rem;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border: none;
          border-radius: 8px;
          cursor: pointer;
          font-weight: 600;
          font-size: 0.875rem;
          transition: all 0.3s ease;
        }

        .btn-sidebar-new:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        .conversations-list {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
          max-height: 400px;
          overflow-y: auto;
        }

        .conversation-item {
          padding: 0.75rem;
          background: var(--bg-secondary);
          border-radius: 6px;
          cursor: pointer;
          transition: all 0.2s ease;
          border-left: 3px solid transparent;
          position: relative;
        }

        .conversation-item:hover {
          background: var(--bg-tertiary);
        }

        .conversation-item.active {
          background: var(--bg-tertiary);
          border-left-color: #667eea;
        }

        .conv-title {
          font-size: 0.875rem;
          font-weight: 500;
          color: var(--text-primary);
          margin-bottom: 0.25rem;
          word-break: break-word;
        }

        .conv-meta {
          font-size: 0.75rem;
          color: var(--text-secondary);
          margin-bottom: 0.5rem;
        }

        .conv-actions {
          display: flex;
          gap: 0.5rem;
          justify-content: flex-end;
        }

        .action-btn {
          background: transparent;
          border: none;
          color: var(--text-secondary);
          cursor: pointer;
          font-size: 0.875rem;
          padding: 0.25rem 0.5rem;
          border-radius: 4px;
          transition: all 0.2s ease;
        }

        .action-btn:hover {
          background: var(--bg-secondary);
          color: var(--text-primary);
        }

        .action-btn.delete:hover {
          color: #ef4444;
        }

        .modal-overlay {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .modal-content {
          background: var(--bg-primary);
          padding: 2rem;
          border-radius: 12px;
          box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
          min-width: 300px;
        }

        .modal-content h3 {
          margin-top: 0;
          color: var(--text-primary);
        }

        .modal-content input {
          width: 100%;
          padding: 0.75rem;
          margin: 1rem 0;
          border: 1px solid var(--border-color);
          border-radius: 6px;
          background: var(--bg-secondary);
          color: var(--text-primary);
          font-size: 0.875rem;
        }

        .modal-content input:focus {
          outline: none;
          border-color: #667eea;
          box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        .modal-buttons {
          display: flex;
          gap: 0.5rem;
          margin-top: 1.5rem;
        }

        .modal-buttons .btn {
          flex: 1;
        }

        .chat-input-area {
          display: flex;
          gap: 0.5rem;
          padding: 1rem;
          background: var(--bg-secondary);
          border-top: 1px solid var(--border-color);
          align-items: center;
        }

        .audio-controls {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .btn-recording {
          background: #ef4444 !important;
          animation: pulse-button 1s infinite;
        }

        @keyframes pulse-button {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }

        .btn-secondary {
          background: #667eea !important;
          color: white !important;
          border: none !important;
        }

        .status {
          font-size: 0.75rem;
          color: var(--text-secondary);
          padding: 0 0.5rem;
        }
      `}</style>
    </div>
  );
}
