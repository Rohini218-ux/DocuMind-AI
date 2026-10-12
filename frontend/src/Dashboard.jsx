
import { useEffect, useRef, useState } from "react";
import { api } from "./services/api";
import "./App.css";
import ReactMarkdown from "react-markdown";
function App({ onLogout }) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadError, setUploadError] = useState("");
  const fileInputRef = useRef(null);

  const [documents, setDocuments] = useState([]);
  const [documentsLoading, setDocumentsLoading] = useState(true);
  const [documentsError, setDocumentsError] = useState("");

  // Load the authenticated user's documents.
  async function loadDocuments() {
    setDocumentsLoading(true);
    setDocumentsError("");

    try {
      const result = await api.getDocuments();

      const documentList = Array.isArray(result)
        ? result
        : result.documents ?? [];

      setDocuments(documentList);
    } catch (err) {
  console.error("Failed to load documents:", err);

  setDocumentsError(
    err.message || "Could not load documents."
  );
} finally {
      setDocumentsLoading(false);
    }
  }

  useEffect(() => {
    loadDocuments();
  }, []);

  // Ask a question using the FastAPI RAG endpoint.
  async function handleAskQuestion(event) {
    event.preventDefault();

    const text = question.trim();

    if (!text || loading) {
      return;
    }

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: text,
      },
    ]);

    setQuestion("");
    setError("");
    setLoading(true);

    try {
      const result = await api.askQuestion(text, 3);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: result.answer,
          sources: result.sources ?? [],
        },
      ]);
    } catch (err) {
      setError(
        err.message ||
          "Unable to get an answer. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }
  
async function handleUpload(event) {
  const file = event.target.files?.[0];

  // Allow the same file to be selected again later.
  event.target.value = "";

  if (!file) return;

  setUploadMessage("");
  setUploadError("");

  if (!file.name.toLowerCase().endsWith(".pdf")) {
    setUploadError("Please select a PDF file.");
    return;
  }

  if (file.size > 10 * 1024 * 1024) {
    setUploadError("The PDF must be 10 MB or smaller.");
    return;
  }

  setUploading(true);

  try {
    await api.uploadDocument(file);
    setUploadMessage("PDF uploaded and processed successfully.");
    await loadDocuments();
  } catch (err) {
    setUploadError(
      err.message || "Upload failed. Please try again."
    );
  } finally {
    setUploading(false);
  }
}


  return (
    <div className="app">
      {/* Sidebar */}
      
<aside className="sidebar">
  <div className="sidebar-brand">
    <span className="brand-icon">📄</span>
    <span>DocuMind AI</span>
  </div>

  <button
    className="new-chat-button"
    type="button"
    onClick={() => {
      setMessages([]);
      setError("");
      setUploadMessage("");
      setUploadError("");
    }}
  >
    <span>＋</span> New chat
  </button>

  <div className="history-section">
    <p className="sidebar-label">RECENT CHATS</p>

    <button className="history-item" type="button">
      <span>▤</span> Document questions
    </button>
  </div>

  <div className="sidebar-account">
    <div className="account-avatar">U</div>

    <div className="account-details">
      <strong>My account</strong>
      <span>DocuMind AI user</span>
    </div>

    <button
      className="logout-button"
      type="button"
      onClick={onLogout}
      title="Log out"
    >
      ↪
    </button>
  </div>
</aside>


      {/* Main content */}
      <main className="main-content">
        <header className="topbar">
          <div>
            <h1>DocuMind AI</h1>
            <p>Ask questions about your documents.</p>
          </div>

          <span className="status">
            ● AI Assistant
          </span>
        </header>

        <div className="workspace">
          {/* Chat panel */}
          <section className="chat-panel">
            <h2>Chat with your documents</h2>

            <p className="muted">
              Ask a question and get an answer from your PDFs.
            </p>

            <div className="messages">
              {messages.length === 0 && (
                <div className="welcome">
                  <span className="welcome-icon">✦</span>

                  <h3>What would you like to know?</h3>

                  <p>
                    Ask something about a document you have uploaded.
                  </p>
                </div>
              )}

              {messages.map((message, index) => (
                <div
                  className={`message ${message.role}`}
                  key={index}
                >
                  <strong>
                    {message.role === "user"
                      ? "You"
                      : "DocuMind AI"}
                  </strong>

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
                            📄{" "}
                            {source.document_name ??
                              `Document ${source.document_id}`}
                          </span>

                          <small>
                            Chunk {source.chunk_id}
                            {" · "}
                            Similarity:{" "}
                            {Number(source.similarity).toFixed(2)}
                          </small>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}

              {loading && (
                <p className="loading" role="status">
                  DocuMind AI is thinking...
                </p>
              )}
            </div>

            {error && (
              <p className="error-message" role="alert">
                {error}
              </p>
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
      title="Upload a PDF"
      disabled={loading || uploading}
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
    />

    <button
      className="send-button"
      type="submit"
      disabled={loading || !question.trim()}
      aria-label="Send message"
    >
      ↑
    </button>
  </div>

  {uploading && <p className="upload-status">Uploading PDF...</p>}
  {uploadMessage && <p className="success-message">{uploadMessage}</p>}
  {uploadError && <p className="error-message">{uploadError}</p>}
</form>

          </section>

          {/* Documents panel */}
          <section className="documents-panel">
            
<div className="panel-heading">
  <h2>Your Documents</h2>

  <button
    type="button"
    className="upload-button"
    disabled={uploading}
    onClick={() => fileInputRef.current?.click()}
  >
    {uploading ? "Uploading..." : "+ Upload PDF"}
  </button>

  <input
    ref={fileInputRef}
    type="file"
    accept=".pdf,application/pdf"
    onChange={handleUpload}
    hidden
  />
</div>

{uploadMessage && (
  <p className="success-message" role="status">
    {uploadMessage}
  </p>
)}

{uploadError && (
  <p className="error-message" role="alert">
    {uploadError}
  </p>
)}


            {documentsLoading && (
              <p className="muted">
                Loading your documents...
              </p>
            )}

            {documentsError && (
              <div>
                <p className="error-message" role="alert">
                  {documentsError}
                </p>

                <button
                  type="button"
                  className="upload-button"
                  onClick={loadDocuments}
                >
                  Try again
                </button>
              </div>
            )}

            {!documentsLoading &&
              !documentsError &&
              documents.length === 0 && (
                <p className="muted">
                  No documents uploaded yet.
                </p>
              )}

            {!documentsLoading &&
              !documentsError &&
              documents.map((document) => (
                <div
                  className="document-item"
                  key={document.id}
                >
                  <span className="pdf-icon">PDF</span>

                  <div>
                    <strong>
                      {document.original_filename ??
                        document.filename ??
                        `Document ${document.id}`}
                    </strong>

                    <p>PDF document</p>
                  </div>
                </div>
              ))}
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;
