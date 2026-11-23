import { useState } from "react";
import axios from "axios";

const API = process.env.REACT_APP_API_URL || "http://localhost:8001";

export default function SearchBar({ onIngested, ingested }) {
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  const ingestTopic = async () => {
    if (!topic.trim()) return;
    setLoading(true);
    setIsError(false);
    setMessage("Searching PubMed and ingesting papers — this may take 30–60 seconds...");
    try {
      const res = await axios.post(`${API}/ingest/pubmed`, { topic });
      setMessage(res.data.message);
      onIngested();
    } catch (e) {
      setIsError(true);
      setMessage(e.response?.data?.detail || "Failed to ingest topic");
    } finally {
      setLoading(false);
    }
  };

  const ingestPDF = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    setIsError(false);
    setMessage("Uploading and processing PDF — please wait...");
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await axios.post(`${API}/ingest/pdf`, form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setMessage(res.data.message);
      onIngested();
    } catch (e) {
      setIsError(true);
      setMessage(e.response?.data?.detail || "Failed to ingest PDF");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-label">{ingested ? "Add more sources" : "Step 1 — Ingest research"}</div>
      <div className="input-row">
        <input
          type="text"
          placeholder="Search medical topic (e.g. metformin diabetes)"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && ingestTopic()}
        />
        <button className="btn-primary" onClick={ingestTopic} disabled={loading}>
          {loading ? "Searching..." : "Search PubMed"}
        </button>
      </div>

      <div className="divider">or</div>

      <label className="upload-label">
        📄 Upload a PDF
        <input type="file" accept=".pdf" onChange={ingestPDF} disabled={loading} />
      </label>

      {message && (
        <div className={`status-msg ${isError ? "error" : ""}`}>
          {loading && <div className="spinner" />}
          {message}
        </div>
      )}
    </div>
  );
}
