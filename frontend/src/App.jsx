import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { FaGithub, FaLinkedinIn, FaInstagram, FaTwitter } from "react-icons/fa";
import Avatar3D from "./Avatar3D";

const API_URL = import.meta.env.VITE_API_URL || "";

// Typewriter component for streaming effect
function TypewriterText({ text, speed = 12, onComplete }) {
  const [displayed, setDisplayed] = useState("");
  const [done, setDone] = useState(false);
  const indexRef = useRef(0);

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
        if (onComplete) onComplete();
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

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingIdx]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    setChatStarted(true);
    const text = input;
    setInput("");

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setIsLoading(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();

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
      setMessages((prev) => {
        setStreamingIdx(prev.length);
        return [
          ...prev,
          { role: "ai", content: "Connection error. Please try again." },
        ];
      });
    } finally {
      setIsLoading(false);
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
        <FaGithub className="social-icon" />
        <FaLinkedinIn className="social-icon" />
        <FaTwitter className="social-icon" />
        <FaInstagram className="social-icon" />
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
            type="text"
            className="chat-input"
            placeholder="Tell me about your skills..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button className="send-btn" onClick={sendMessage}>
            ➤
          </button>
        </div>
      </div>
    </div>
  );
}
