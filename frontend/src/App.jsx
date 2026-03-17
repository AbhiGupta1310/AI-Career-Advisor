import { useState, useRef, useEffect, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import { FaGithub, FaLinkedinIn, FaMedium, FaGlobe } from "react-icons/fa";
import Avatar3D from "./Avatar3D";

const API_URL = import.meta.env.VITE_API_URL || "";

// Typewriter component for streaming effect
function TypewriterText({ text, speed = 12, onComplete }) {
  const [displayed, setDisplayed] = useState("");
  const [done, setDone] = useState(false);
  const indexRef = useRef(0);
  const onCompleteRef = useRef(onComplete);

  // Keep callback ref in sync without triggering re-render
  useEffect(() => {
    onCompleteRef.current = onComplete;
  }, [onComplete]);

  useEffect(() => {
    if (!text) return;
    indexRef.current = 0;
    setDisplayed("");
    setDone(false);

    const interval = setInterval(() => {
      indexRef.current += 1;
      const next = text.slice(0, indexRef.current);
      setDisplayed(next);

      if (indexRef.current >= text.length) {
        clearInterval(interval);
        setDone(true);
        if (onCompleteRef.current) onCompleteRef.current();
      }
    }, speed);

    return () => clearInterval(interval);
  }, [text, speed]);

  return (
    <div>
      <ReactMarkdown>{displayed}</ReactMarkdown>
      {!done && <span className="typing-cursor" />}
    </div>
  );
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [chatStarted, setChatStarted] = useState(false);
  const [streamingIdx, setStreamingIdx] = useState(-1);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingIdx]);

  // Re-focus input after AI response finishes loading
  useEffect(() => {
    if (!isLoading && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isLoading]);

  const sendMessage = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    setChatStarted(true);
    setInput("");

    // Build the updated message list including the new user message
    const userMsg = { role: "user", content: trimmed };
    const updatedMessages = [...messages, userMsg];

    setMessages(updatedMessages);
    setIsLoading(true);

    try {
      // Only send role + content in history (strip extra fields like predicted, skills)
      const cleanHistory = updatedMessages.map(({ role, content }) => ({
        role,
        content,
      }));

      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: trimmed,
          history: cleanHistory,
        }),
      });

      const data = await res.json();

      // Check for server error responses (500, 503, 422, etc.)
      if (!res.ok) {
        // Pydantic 422 errors return detail as an array of objects
        let errorDetail = data.detail;
        if (Array.isArray(errorDetail)) {
          errorDetail = errorDetail.map((e) => e.msg || JSON.stringify(e)).join("; ");
        }
        throw new Error(errorDetail || `Server error (${res.status})`);
      }

      setMessages((prev) => {
        setStreamingIdx(prev.length);
        return [
          ...prev,
          {
            role: "ai",
            content: data.response,
            predicted: data.predicted_profile,
            skills: data.recommended_skills,
          },
        ];
      });
    } catch (err) {
      const errorMsg =
        err.message && err.message !== "Failed to fetch"
          ? err.message
          : "Connection error. Please check if the server is running and try again.";

      setMessages((prev) => {
        setStreamingIdx(prev.length);
        return [
          ...prev,
          { role: "ai", content: `⚠️ ${errorMsg}` },
        ];
      });
    } finally {
      setIsLoading(false);
    }
  }, [input, isLoading, messages]);

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className={`app-container ${chatStarted ? "chat-mode" : ""}`}>
      <div className="particles"></div>

      {/* Navbar */}
      <nav className="navbar">
        <div className="logo">
          CAREER.AI <span className="status-dot"></span>
        </div>
      </nav>

      {/* Social Sidebar */}
      <aside className="social-sidebar">
        <a
          href="https://github.com/AbhiGupta1310"
          target="_blank"
          rel="noopener noreferrer"
        >
          <FaGithub className="social-icon" />
        </a>
        <a
          href="https://www.linkedin.com/in/abhi-gupta-data-science/"
          target="_blank"
          rel="noopener noreferrer"
        >
          <FaLinkedinIn className="social-icon" />
        </a>
        <a
          href="https://medium.com/@abhigupta5064"
          target="_blank"
          rel="noopener noreferrer"
        >
          <FaMedium className="social-icon" />
        </a>
        <a
          href="https://abhi-gupta.me/"
          target="_blank"
          rel="noopener noreferrer"
        >
          <FaGlobe className="social-icon" />
        </a>
      </aside>

      {/* Left Panel: Hero text + Robot */}
      <div className="left-panel">
        {!chatStarted && (
          <div className="hero-text">
            <div className="hero-subtitle">HELLO! I'M CAREER INTELLIGENCE</div>
            <h1 className="hero-title">
              <span>YOUR PERSONAL</span>
              <span style={{ color: "#a855f7" }}>AI CAREER MENTOR</span>
            </h1>
            <p className="hero-desc">
              I analyze your skills, predict your ideal role, and guide you with
              personalized validation. Powered by XGBoost & Groq Llama 3.3.
            </p>
          </div>
        )}

        <div className="robot-container">
          <div className="glow-circle"></div>
          <Avatar3D />
        </div>
      </div>

      {/* Right Panel: Chat messages (only visible after chat starts) */}
      {chatStarted && (
        <div className="right-panel active">
          <div className="chat-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`msg ${msg.role}`}>
                {msg.role === "ai" && i === streamingIdx ? (
                  <TypewriterText
                    text={msg.content}
                    speed={12}
                    onComplete={() => setStreamingIdx(-1)}
                  />
                ) : (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="msg ai">
                <span className="typing-cursor" /> Thinking...
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      )}

      {/* Chat Input: Always visible at bottom */}
      <div className={`chat-input-wrapper ${chatStarted ? "chat-active" : ""}`}>
        <div className="chat-input-container">
          <input
            ref={inputRef}
            type="text"
            className="chat-input"
            placeholder={
              isLoading
                ? "Waiting for response..."
                : "Tell me about your skills..."
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
          />
          <button
            className={`send-btn ${isLoading ? "send-btn-disabled" : ""}`}
            onClick={sendMessage}
            disabled={isLoading}
          >
            ➤
          </button>
        </div>
      </div>
    </div>
  );
}
