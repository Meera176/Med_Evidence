import { useState } from "react";
import axios from "axios";
import Answer from "./components/Answer";
import "./App.css";

const API = process.env.REACT_APP_API_URL || "http://localhost:8001";

const DNAIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" strokeWidth="1.8" strokeLinecap="round">
    <path d="M5 3c0 4 14 4 14 8S5 15 5 19" />
    <path d="M19 3c0 4-14 4-14 8s14 4 14 8" />
    <line x1="5" y1="9" x2="19" y2="9" />
    <line x1="5" y1="15" x2="19" y2="15" />
  </svg>
);

const MoleculeIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#06b6d4" strokeWidth="1.8" strokeLinecap="round">
    <circle cx="12" cy="12" r="2" />
    <circle cx="5" cy="6" r="2" />
    <circle cx="19" cy="6" r="2" />
    <circle cx="5" cy="18" r="2" />
    <circle cx="19" cy="18" r="2" />
    <line x1="7" y1="7" x2="10" y2="10" />
    <line x1="17" y1="7" x2="14" y2="10" />
    <line x1="7" y1="17" x2="10" y2="14" />
    <line x1="17" y1="17" x2="14" y2="14" />
  </svg>
);

const BrainIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#8b5cf6" strokeWidth="1.8" strokeLinecap="round">
    <path d="M9.5 2a2.5 2.5 0 0 1 5 0v1a2.5 2.5 0 0 1 2.5 2.5 2.5 2.5 0 0 1 2.5 2.5 2.5 2.5 0 0 1-2.5 2.5v1a2.5 2.5 0 0 1-5 0v-1a2.5 2.5 0 0 1-2.5-2.5 2.5 2.5 0 0 1-2.5-2.5A2.5 2.5 0 0 1 9.5 3z" />
    <path d="M12 9v6M9 12h6" />
  </svg>
);

const CitationIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="1.8" strokeLinecap="round">
    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
    <polyline points="14 2 14 8 20 8" />
    <line x1="9" y1="13" x2="15" y2="13" />
    <line x1="9" y1="17" x2="13" y2="17" />
  </svg>
);

const HeroIllustration = () => (
  <svg width="120" height="120" viewBox="0 0 120 120" fill="none">
    <circle cx="60" cy="60" r="50" stroke="rgba(59,130,246,0.15)" strokeWidth="1" />
    <circle cx="60" cy="60" r="35" stroke="rgba(59,130,246,0.2)" strokeWidth="1" />
    <circle cx="60" cy="60" r="20" stroke="rgba(59,130,246,0.3)" strokeWidth="1" />
    <circle cx="60" cy="60" r="6" fill="rgba(59,130,246,0.6)" />
    {[0,60,120,180,240,300].map((deg, i) => {
      const rad = (deg * Math.PI) / 180;
      const x = 60 + 35 * Math.cos(rad);
      const y = 60 + 35 * Math.sin(rad);
      return <circle key={i} cx={x} cy={y} r="4" fill={i % 2 === 0 ? "rgba(6,182,212,0.7)" : "rgba(139,92,246,0.7)"} />;
    })}
    {[0,60,120,180,240,300].map((deg, i) => {
      const rad = (deg * Math.PI) / 180;
      const x = 60 + 50 * Math.cos(rad);
      const y = 60 + 50 * Math.sin(rad);
      return <circle key={i} cx={x} cy={y} r="3" fill="rgba(59,130,246,0.4)" />;
    })}
  </svg>
);

export default function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pdfMessage, setPdfMessage] = useState("");
  const [pdfLoading, setPdfLoading] = useState(false);

  const askQuestion = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setAnswer(null);
    try {
      const res = await axios.post(`${API}/ask`, { question });
      setAnswer(res.data);
    } catch (e) {
      setAnswer({ error: e.response?.data?.detail || "Failed to get answer" });
    } finally {
      setLoading(false);
    }
  };

  const uploadPDF = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setPdfLoading(true);
    setPdfMessage("Uploading PDF...");
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await axios.post(`${API}/ingest/pdf`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setPdfMessage(res.data.message);
    } catch (e) {
      setPdfMessage(e.response?.data?.detail || "Failed to upload PDF");
    } finally {
      setPdfLoading(false);
    }
  };

  return (
    <>
      <nav className="nav">
        <span className="nav-logo">MedEvidence</span>
        <label className="upload-label" style={{ cursor: "pointer" }}>
          {pdfLoading ? "Uploading..." : "📄 Upload PDF"}
          <input type="file" accept=".pdf" onChange={uploadPDF} disabled={pdfLoading} />
        </label>
      </nav>

      {!answer && !loading && (
        <>
          <section className="hero">
            <div className="hero-glow" />
            <div className="hero-badge">⚕ AI-Powered Medical Research</div>
            <h1>Evidence-based answers<br />from <span>published research</span></h1>
            <p>Ask any medical question — we automatically fetch relevant papers from PubMed and answer with citations.</p>
          </section>

          <div className="bento">
            <div className="bento-card wide illus">
              <HeroIllustration />
              <div style={{ marginLeft: "1.5rem", textAlign: "left" }}>
                <div className="bento-stat">20M+</div>
                <p style={{ color: "var(--text)", fontWeight: 500, marginBottom: "0.25rem" }}>PubMed Articles</p>
                <p>Instantly search and ingest peer-reviewed medical literature</p>
              </div>
            </div>
            <div className="bento-card">
              <div className="bento-icon icon-purple"><BrainIcon /></div>
              <h3>AI Reasoning</h3>
              <p>LLM reads the papers and answers your question with context</p>
            </div>
            <div className="bento-card">
              <div className="bento-icon icon-blue"><DNAIcon /></div>
              <h3>Auto Fetch</h3>
              <p>Automatically fetches relevant papers from PubMed for your question</p>
            </div>
            <div className="bento-card">
              <div className="bento-icon icon-cyan"><MoleculeIcon /></div>
              <h3>PDF Support</h3>
              <p>Upload your own research papers and query them directly</p>
            </div>
            <div className="bento-card">
              <div className="bento-icon icon-green"><CitationIcon /></div>
              <h3>Cited Answers</h3>
              <p>Every answer links back to the source paper and page number</p>
            </div>
          </div>
        </>
      )}

      <div className="workflow">
        {pdfMessage && (
          <div className="card" style={{ padding: "0.75rem 1.5rem" }}>
            <p className="status-msg">{pdfMessage}</p>
          </div>
        )}

        <div className="card">
          <div className="card-label">Ask a medical question</div>
          <div className="question-row">
            <input
              type="text"
              placeholder="e.g. What are the symptoms of PCOS?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && askQuestion()}
            />
            <button className="btn-primary" onClick={askQuestion} disabled={loading}>
              {loading ? (
                <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                  <span className="spinner" style={{ borderTopColor: "white", borderColor: "rgba(255,255,255,0.3)" }} />
                  Searching...
                </span>
              ) : "Ask"}
            </button>
          </div>
          {loading && (
            <p className="status-msg">
              <span className="spinner" />
              Fetching papers from PubMed and generating answer...
            </p>
          )}
        </div>

        <Answer data={answer} onReset={() => { setAnswer(null); setQuestion(""); }} />
      </div>
    </>
  );
}
