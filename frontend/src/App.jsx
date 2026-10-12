
import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { api } from "./services/api";
import AuthPage from "./AuthPage";
import "./App.css";

function loadSavedChats() {
  try {
    return JSON.parse(localStorage.getItem("documind_chats") || "[]");
  } catch {
    return [];
  }
}

function App() {
  const [authenticated, setAuthenticated] = useState(
    () => Boolean(localStorage.getItem("access_token"))
  );

  const [chats, setChats] = useState(loadSavedChats);
  const [activeChatId, setActiveChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [uploadMessage, setUploadMessage] = useState("");

  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  // Persist chat history in this browser.
  useEffect(() => {
    localStorage.setItem("documind_chats", JSON.stringify(chats));
  }, [chats]);

  // Show the login page if an API request returns 401.
  useEffect(() => {
    function handleUnauthorized() {
      api.logout();
      setAuthenticated(false);
      setMessages([]);
      setActiveChatId(null);
      setError("Your session expired. Please log in again.");
    }

    window.addEventListener("auth:unauthorized", handleUnauthorized);

    return () => {
      window.removeEventListener(
        "auth:unauthorized",
        handleUnauthorized
      );
    };
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function handleLogin() {
    setAuthenticated(true);
    setMessages([]);
    setActiveChatId(null);
    setQuestion("");
    setError("");
    setUploadMessage("");
  }

  function handleLogout() {
    api.logout();
    setAuthenticated(false);
    setMessages([]);
    setActiveChatId(null);
    setQuestion("");
    setError("");
    setUploadMessage("");
    setLoading(false);
    setUploading(false);
  }

  function createNewChat() {
    setActiveChatId(null);
    setMessages([]);
    setQuestion("");
    setError("");
    setUploadMessage("");
  }

  function selectChat(chat) {
    setActiveChatId(chat.id);
    setMessages(chat.messages || []);
    setQuestion("");
    setError("");
    setUploadMessage("");
  }

  function saveChat(updatedMessages, chatId, title) {
    setChats((previous) => {
      const existing = previous.find((chat) => chat.id === chatId);

      if (existing) {
        return [
          {
            ...existing,
            title: existing.title || title,
            messages: updatedMessages,
          },
          ...previous.filter((chat) => chat.id !== chatId),
        ];
      }

      return [
        {
          id: chatId,
          title,
          messages: updatedMessages,
        },
        ...previous,
      ];
    });
  }

  async function handleAskQuestion(event) {
    event.preventDefault();

    const text = question.trim();
    if (!text || loading) return;

    const chatId = activeChatId ?? Date.now();
    const title =
      text.length > 35 ? `${text.slice(0, 35)}...` : text;

    const userMessage = { role: "user", content: text };
    const updatedMessages = [...messages, userMessage];

    setActiveChatId(chatId);
    setMessages(updatedMessages);
    setQuestion("");
    setError("");
    setUploadMessage("");
    setLoading(true);

    saveChat(updatedMessages, chatId, title);

    try {
      const result = await api.askQuestion(text, 3);

      const assistantMessage = {
        role: "assistant",
        content: result.answer || "I couldn't generate an answer.",
        sources: result.sources ?? [],
      };

      const finalMessages = [...updatedMessages, assistantMessage];

      setMessages(finalMessages);
      saveChat(finalMessages, chatId, title);
    } catch (err) {
      setError(err.message || "Unable to get an answer. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    if (
      file.type !== "application/pdf" &&
      !file.name.toLowerCase().endsWith(".pdf")
    ) {
      setError("Please select a PDF file.");
      event.target.value = "";
      return;
    }

    setUploading(true);
    setError("");
    setUploadMessage("");

    try {
      const result = await api.uploadDocument(file);
      setUploadMessage(
        result?.message || `${file.name} uploaded successfully.`
      );
    } catch (err) {
      setError(err.message || "PDF upload failed. Please try again.");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  // Do not render the chat unless a frontend login has succeeded.
  if (!authenticated) {
    return <AuthPage onLogin={handleLogin} />;
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-icon">▤</span>
          <span>DocuMind AI</span>
        </div>

        <button
          className="new-chat-button"
          type="button"
          onClick={createNewChat}
        >
          <span>＋</span> New chat
        </button>

        <div className="history-heading">RECENT CHATS</div>

        <div className="chat-history">
          {chats.map((chat) => (
            <button
              key={chat.id}
              type="button"
              className={`history-item ${
                activeChatId === chat.id ? "selected" : ""
              }`}
              onClick={() => selectChat(chat)}
              title={chat.title}
            >
              <span>▤</span>
              <span className="history-title">{chat.title}</span>
            </button>
          ))}
        </div>

        <div className="account-area">
          <div className="avatar">U</div>

          <div className="account-details">
            <strong>My account</strong>
            <span>DocuMind AI user</span>
          </div>

          <button
            className="logout-button"
            type="button"
            title="Logout"
            aria-label="Logout"
            onClick={handleLogout}
          >
            ↪
          </button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <h1>DocuMind AI</h1>
            <p>Ask questions about your documents.</p>
          </div>
        </header>

        <section className="chat-panel">
          <div className="messages">
            {messages.length === 0 && (
              <div className="welcome">
                <div className="welcome-icon">✦</div>
                <h2>What would you like to know?</h2>
                <p>
                  Ask a question, summarize a PDF, or explore its key ideas.
                </p>
              </div>
            )}

            {messages.map((message, index) => (
              <article
                className={`message ${message.role}`}
                key={`${activeChatId}-${index}`}
              >
                <div className="message-label">
                  {message.role === "user" ? "You" : "DocuMind AI"}
                </div>

                <div className="markdown-content">
                  <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>

                {message.sources?.length > 0 && (
                  <div className="sources">
                    <strong>Sources</strong>

                    {message.sources.map((source) => (
                      <div
                        className="source-item"
                        key={`${source.document_id}-${source.chunk_id}`}
                      >
                        <span>
                          {source.document_name ||
                            `Document ${source.document_id}`}
                        </span>
                        <small>Chunk {source.chunk_id}</small>
                      </div>
                    ))}
                  </div>
                )}
              </article>
            ))}

            {loading && (
              <div className="thinking" role="status">
                <span className="thinking-dot" />
                DocuMind AI is thinking...
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {error && (
            <div className="feedback error-message" role="alert">
              {error}
            </div>
          )}

          {uploadMessage && (
            <div className="feedback success-message" role="status">
              {uploadMessage}
            </div>
          )}

          <form className="chat-form" onSubmit={handleAskQuestion}>
            <div className="chat-input-box">
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,application/pdf"
                hidden
                onChange={handleUpload}
              />

              <button
                type="button"
                className="attach-button"
                title="Upload PDF"
                aria-label="Upload PDF"
                disabled={uploading}
                onClick={() => fileInputRef.current?.click()}
              >
                ＋
              </button>

              <input
                className="question-input"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                placeholder="Ask anything about your documents..."
                disabled={loading}
                aria-label="Your question"
              />

              <button
                type="submit"
                className="send-button"
                disabled={loading || !question.trim()}
                aria-label="Send message"
              >
                ↑
              </button>
            </div>

            {uploading && (
              <p className="upload-progress">
                Uploading and processing PDF...
              </p>
            )}
          </form>
        </section>
      </main>
    </div>
  );
}

export default App;
