import { useState, useRef, useEffect, useCallback } from "react";
import ReactMarkdown from "react-markdown";
import { FaGithub, FaLinkedinIn, FaMedium, FaGlobe } from "react-icons/fa";

const API_URL = import.meta.env.VITE_API_URL || "";

// ─── Typewriter ────────────────────────────────────────────────────────────────
function TypewriterText({ text, speed = 10, onComplete }) {
  const [displayed, setDisplayed] = useState("");
  const [done, setDone] = useState(false);
  const indexRef = useRef(0);
  const onCompleteRef = useRef(onComplete);

  useEffect(() => { onCompleteRef.current = onComplete; }, [onComplete]);

  useEffect(() => {
    if (!text) return;
    indexRef.current = 0;
    setDisplayed("");
    setDone(false);

    const interval = setInterval(() => {
      indexRef.current += 1;
      setDisplayed(text.slice(0, indexRef.current));
      if (indexRef.current >= text.length) {
        clearInterval(interval);
        setDone(true);
        onCompleteRef.current?.();
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

// ─── Background ────────────────────────────────────────────────────────────────
function Background() {
  return <div className="bg-canvas" aria-hidden="true" />;
}

// ─── Send Icon ─────────────────────────────────────────────────────────────────
function SendIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="2.5"
      strokeLinecap="round" strokeLinejoin="round">
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  );
}

// ─── App ───────────────────────────────────────────────────────────────────────
export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [chatStarted, setChatStarted] = useState(false);
  const [streamingIdx, setStreamingIdx] = useState(-1);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingIdx]);

  useEffect(() => {
    if (!isLoading) inputRef.current?.focus();
  }, [isLoading]);

  const sendMessage = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading) return;

    setChatStarted(true);
    setInput("");

    const userMsg = { role: "user", content: trimmed };
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setIsLoading(true);

    try {
      const cleanHistory = updatedMessages.map(({ role, content }) => ({ role, content }));

      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed, history: cleanHistory }),
      });

      const data = await res.json();

      if (!res.ok) {
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
        return [...prev, { role: "ai", content: `⚠️ ${errorMsg}` }];
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
    <div className="app-container">
      <Background />

      {/* ── Navbar ── */}
      <nav className="navbar">
        <div className="logo">
          <div className="logo-icon">
            {/* Simple career/chart icon */}
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none"
              stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
            </svg>
          </div>
          Career.AI
        </div>
        <div className="status-pill">
          <span className="status-dot" />
          Online
        </div>
      </nav>

      {/* ── Social Sidebar ── */}
      <aside className="social-sidebar" aria-label="Social links">
        <a href="https://github.com/AbhiGupta1310" target="_blank" rel="noopener noreferrer" className="social-link" aria-label="GitHub">
          <FaGithub className="social-icon" />
        </a>
        <a href="https://www.linkedin.com/in/abhi-gupta-data-science/" target="_blank" rel="noopener noreferrer" className="social-link" aria-label="LinkedIn">
          <FaLinkedinIn className="social-icon" />
        </a>
        <a href="https://medium.com/@abhigupta5064" target="_blank" rel="noopener noreferrer" className="social-link" aria-label="Medium">
          <FaMedium className="social-icon" />
        </a>
        <a href="https://abhi-gupta.me/" target="_blank" rel="noopener noreferrer" className="social-link" aria-label="Website">
          <FaGlobe className="social-icon" />
        </a>
      </aside>

      {/* ── Hero ── */}
      {!chatStarted && (
        <main className="main-content">
          <section className="hero-section">

            {/* Eyebrow */}
            <div className="hero-badge">
              <span className="hero-badge-dot" />
              AI-powered career guidance
            </div>

            {/* Title — serif, mixed italic like Steep */}
            <h1 className="hero-title">
              Your personal guide to{" "}
              <span className="hero-title-italic">smarter careers</span>
            </h1>

            <p className="hero-description">
              Career.AI analyzes your skills, predicts your ideal career path,
              and delivers personalized guidance — powered by machine learning
              and modern LLM technology.
            </p>

            {/* Feature chips */}
            <div className="hero-features">
              <div className="feature-item">
                <div className="feature-icon">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10" /><path d="M12 8v4l3 3" />
                  </svg>
                </div>
                <span>Skill Analysis</span>
              </div>
              <div className="feature-item">
                <div className="feature-icon">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                  </svg>
                </div>
                <span>Career Prediction</span>
              </div>
              <div className="feature-item">
                <div className="feature-icon">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                  </svg>
                </div>
                <span>Personalized Advice</span>
              </div>
            </div>

            {/* Stats */}
            <div className="hero-stats">
              <div className="stat-item">
                <div className="stat-number">12+</div>
                <div className="stat-label">Career Tracks</div>
              </div>
              <div className="stat-divider" />
              <div className="stat-item">
                <div className="stat-number">ML</div>
                <div className="stat-label">Powered</div>
              </div>
              <div className="stat-divider" />
              <div className="stat-item">
                <div className="stat-number">24/7</div>
                <div className="stat-label">Available</div>
              </div>
            </div>

          </section>
        </main>
      )}

      {/* ── Chat ── */}
      {chatStarted && (
        <div className="right-panel active">
          <div className="chat-messages" role="log" aria-live="polite">
            {messages.map((msg, i) => (
              <div key={i} className={`msg ${msg.role}`}>
                {msg.role === "ai" && i === streamingIdx ? (
                  <TypewriterText
                    text={msg.content}
                    speed={10}
                    onComplete={() => setStreamingIdx(-1)}
                  />
                ) : (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                )}
              </div>
            ))}

            {isLoading && (
              <div className="thinking-indicator">
                <div className="thinking-dots">
                  <span className="thinking-dot" />
                  <span className="thinking-dot" />
                  <span className="thinking-dot" />
                </div>
                <span className="thinking-label">Thinking…</span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>
      )}

      {/* ── Input ── */}
      <div className="chat-input-wrapper">
        <div className="chat-input-container">
          <input
            ref={inputRef}
            type="text"
            className="chat-input"
            placeholder={
              isLoading
                ? "Waiting for response…"
                : "Tell me about your skills and experience…"
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            aria-label="Chat input"
          />
          <button
            className="send-btn"
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            aria-label="Send message"
          >
            <SendIcon />
          </button>
        </div>
        <p className="input-hint">Enter to send · Shift+Enter for new line</p>
      </div>
    </div>
  );
}
