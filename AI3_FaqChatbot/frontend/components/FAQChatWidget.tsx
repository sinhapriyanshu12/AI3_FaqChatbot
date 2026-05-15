import React, { useState, useRef, useEffect } from "react";

interface Message {
  role: "user" | "bot";
  text: string;
  sources?: string[];
}

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/ai/faq";

export default function FAQChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "bot",
      text: "Hi! I'm the KALNET School Assistant. Ask me anything about admissions, fees, or school rules.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg: Message = { role: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: input,
          history: messages.map((m) => ({ role: m.role, content: m.text })),
        }),
      });
      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: data.answer, sources: data.sources },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "bot", text: "Sorry, I could not connect to the server. Please try again." },
      ]);
    }
    setLoading(false);
  };

  return (
    <div style={{ position: "fixed", bottom: 24, right: 24, zIndex: 9999, fontFamily: "sans-serif" }}>
      {open && (
        <div style={{
          width: 370,
          height: 500,
          background: "#ffffff",
          borderRadius: 16,
          boxShadow: "0 8px 32px rgba(0,0,0,0.18)",
          display: "flex",
          flexDirection: "column",
          marginBottom: 12,
          overflow: "hidden",
        }}>
          {/* Header */}
          <div style={{
            padding: "14px 18px",
            background: "#1a73e8",
            color: "#fff",
            fontWeight: 600,
            fontSize: 15,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}>
            <span>KALNET School Assistant</span>
            <span
              onClick={() => setOpen(false)}
              style={{ cursor: "pointer", fontSize: 18, opacity: 0.8 }}
            >✕</span>
          </div>

          {/* Messages */}
          <div style={{
            flex: 1,
            overflowY: "auto",
            padding: "12px 14px",
            display: "flex",
            flexDirection: "column",
            gap: 10,
            background: "#f8f9fa",
          }}>
            {messages.map((m, i) => (
              <div key={i} style={{
                alignSelf: m.role === "user" ? "flex-end" : "flex-start",
                maxWidth: "82%",
              }}>
                <div style={{
                  padding: "10px 14px",
                  borderRadius: m.role === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
                  background: m.role === "user" ? "#1a73e8" : "#ffffff",
                  color: m.role === "user" ? "#fff" : "#202124",
                  fontSize: 14,
                  lineHeight: 1.5,
                  boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                }}>
                  {m.text}
                </div>
                {m.sources && m.sources.length > 0 && (
                  <div style={{ fontSize: 11, color: "#888", marginTop: 3, paddingLeft: 4 }}>
                    Source: {m.sources.join(", ")}
                  </div>
                )}
              </div>
            ))}
            {loading && (
              <div style={{
                alignSelf: "flex-start",
                padding: "10px 14px",
                background: "#ffffff",
                borderRadius: "16px 16px 16px 4px",
                fontSize: 14,
                color: "#888",
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
              }}>
                Typing...
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div style={{
            display: "flex",
            padding: "10px 12px",
            borderTop: "1px solid #e8eaed",
            gap: 8,
            background: "#fff",
          }}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              placeholder="Ask a question..."
              style={{
                flex: 1,
                padding: "9px 14px",
                borderRadius: 22,
                border: "1px solid #dadce0",
                outline: "none",
                fontSize: 14,
                background: "#f8f9fa",
              }}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              style={{
                padding: "9px 18px",
                background: loading || !input.trim() ? "#dadce0" : "#1a73e8",
                color: "#fff",
                border: "none",
                borderRadius: 22,
                cursor: loading || !input.trim() ? "not-allowed" : "pointer",
                fontSize: 14,
                fontWeight: 500,
              }}
            >
              Send
            </button>
          </div>
        </div>
      )}

      {/* Floating button */}
      <button
        onClick={() => setOpen((o) => !o)}
        style={{
          width: 58,
          height: 58,
          borderRadius: "50%",
          background: "#1a73e8",
          border: "none",
          cursor: "pointer",
          color: "#fff",
          fontSize: 24,
          boxShadow: "0 4px 14px rgba(26,115,232,0.5)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          transition: "transform 0.2s",
        }}
        title="Ask school assistant"
      >
        {open ? "✕" : "💬"}
      </button>
    </div>
  );
}
