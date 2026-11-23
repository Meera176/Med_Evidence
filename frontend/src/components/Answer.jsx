export default function Answer({ data, onReset }) {
  if (!data) return null;
  if (data.error) return <div className="error-card">{data.error}</div>;

  const sections = parseAnswer(data.answer);

  return (
    <div className="card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem" }}>
        <div className="card-label" style={{ margin: 0 }}>Answer</div>
        <button className="btn-ghost" onClick={onReset} style={{ fontSize: "0.78rem", padding: "0.3rem 0.8rem" }}>
          Ask another
        </button>
      </div>

      {sections.map((section, i) => (
        <div key={i} className="answer-section">
          {section.heading && <div className="answer-heading">{section.heading}</div>}
          {section.items.map((item, j) => (
            <div key={j} className={`answer-item ${item.type}`}>
              {item.type === "bullet" ? (
                <span>• {item.text}</span>
              ) : (
                <p>{item.text}</p>
              )}
            </div>
          ))}
        </div>
      ))}

      {data.citations?.length > 0 && (
        <>
          <div className="section-label">Sources</div>
          <div className="citations-grid">
            {data.citations.map((c, i) => (
              <div key={i} className="citation-chip">
                <span>[{i + 1}] {c.source}</span>
                page {c.page}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

function parseAnswer(text) {
  const lines = text.split("\n").filter(l => l.trim());
  const sections = [];
  let current = { heading: null, items: [] };

  for (const line of lines) {
    if (line.startsWith("## ")) {
      if (current.items.length > 0 || current.heading) sections.push(current);
      current = { heading: line.replace("## ", ""), items: [] };
    } else if (line.startsWith("- ") || line.startsWith("* ")) {
      current.items.push({ type: "bullet", text: line.replace(/^[-*] /, "") });
    } else if (line.trim()) {
      current.items.push({ type: "text", text: line.trim() });
    }
  }
  if (current.items.length > 0 || current.heading) sections.push(current);
  return sections;
}
