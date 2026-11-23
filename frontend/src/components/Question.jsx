import { useState } from "react";
import axios from "axios";

const API = process.env.REACT_APP_API_URL || "http://localhost:8001";

export default function Question({ onAnswer }) {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  const ask = async () => {
    if (!question.trim()) return;
    setLoading(true);
    try {
      const res = await axios.post(`${API}/ask`, { question });
      onAnswer(res.data);
    } catch (e) {
      onAnswer({ error: e.response?.data?.detail || "Failed to get answer" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-label">Step 2 — Ask a question</div>
      <div className="question-row">
        <input
          type="text"
          placeholder="Ask a medical question about the ingested papers..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && ask()}
        />
        <button className="btn-primary" onClick={ask} disabled={loading}>
          {loading ? (
            <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
              <span className="spinner" style={{ borderTopColor: "white", borderColor: "rgba(255,255,255,0.3)" }} />
              Thinking...
            </span>
          ) : "Ask"}
        </button>
      </div>
    </div>
  );
}
