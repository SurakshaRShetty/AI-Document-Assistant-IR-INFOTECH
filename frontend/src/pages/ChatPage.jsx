import { useState } from "react";
import api from "../api/axios";
import Header from "../components/Header";

export default function ChatPage() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [error, setError] = useState("");
  const [conversationId, setConversationId] = useState(
    localStorage.getItem("conversation_id")
      ? Number(localStorage.getItem("conversation_id"))
      : null
  );

  const ask = async () => {
    const documentId = localStorage.getItem("document_id");

    if (!documentId) {
      setError("Please upload a document first");
      return;
    }

    try {
      const res = await api.post("/chat/ask", {
        document_id: Number(documentId),
        question,
        conversation_id: conversationId,
      });

      setAnswer(res.data.answer);
      setSources(res.data.sources || []);
      setConversationId(res.data.conversation_id);
      localStorage.setItem("conversation_id", res.data.conversation_id);
      setError("");
    } catch {
      setError("Failed to get answer");
    }
  };

  return (
    <>
      <Header />

      <div style={styles.page}>
        <div style={styles.card}>
          <h2>Chat with your Document</h2>

          <textarea
            style={styles.textarea}
            placeholder="Ask a question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />

          <button style={styles.button} onClick={ask}>
            Ask
          </button>

          {error && <p style={styles.error}>{error}</p>}

          {answer && (
            <div style={styles.answerBox}>
              <b>Answer:</b>
              <p>{answer}</p>
            </div>
          )}

          {sources.length > 0 && (
            <div style={styles.sourcesBox}>
              <b>Sources:</b>
              <ul style={styles.sourcesList}>
                {sources.map((s) => (
                  <li key={s.chunk_id}>
                    {s.filename} — page {s.page_number} (chunk {s.chunk_id})
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

const styles = {
  page: {
    background: "#f5f7fb",
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    paddingTop: "40px",
  },
  card: {
    background: "#fff",
    width: "700px",
    padding: "30px",
    borderRadius: "10px",
    boxShadow: "0 10px 25px rgba(0,0,0,0.1)",
  },
  textarea: {
    width: "100%",
    height: "120px",
    padding: "12px",
    borderRadius: "6px",
    border: "1px solid #ccc",
    marginBottom: "12px",
  },
  button: {
    background: "#2563eb",
    color: "#fff",
    border: "none",
    padding: "10px 18px",
    borderRadius: "6px",
    cursor: "pointer",
  },
  error: {
    color: "red",
    marginTop: "10px",
  },
  answerBox: {
    background: "#f1f5f9",
    padding: "15px",
    borderRadius: "6px",
    marginTop: "20px",
  },
  sourcesBox: {
    marginTop: "12px",
    padding: "12px 15px",
    background: "#fafafa",
    border: "1px solid #e5e7eb",
    borderRadius: "6px",
    fontSize: "13px",
    color: "#444",
  },
  sourcesList: {
    margin: "6px 0 0 0",
    paddingLeft: "18px",
  },
};
