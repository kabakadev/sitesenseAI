import { useEffect, useState } from "react";
import type { FormEvent } from "react";

import {
  createAnalysis,
  getAnalyses,
  getHealth,
} from "./services/api";
import type { Analysis } from "./services/api";

function parseItems(value: string): string[] {
  try {
    const parsed: unknown = JSON.parse(value);
    return Array.isArray(parsed) ? parsed.filter((item): item is string => typeof item === "string") : [];
  } catch {
    return [value];
  }
}

export default function App() {
  const [apiStatus, setApiStatus] = useState("Connecting to API...");
  const [input, setInput] = useState("");
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [selected, setSelected] = useState<Analysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([getHealth(), getAnalyses()])
      .then(([, history]) => {
        setApiStatus("API connected");
        setAnalyses(history);
      })
      .catch(() => setApiStatus("API unavailable"));
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!input.trim()) return;
    setLoading(true);
    setError("");
    try {
      const result = await createAnalysis(input.trim());
      setAnalyses((current) => [result, ...current]);
      setSelected(result);
      setInput("");
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <header>
        <p>SiteSense · Gemma analysis demo</p>
        <span aria-live="polite">{apiStatus}</span>
      </header>
      <h1>Turn a site idea into useful next steps.</h1>
      <p>Describe a website, product, or problem and Gemma will return findings and recommendations.</p>
      <form onSubmit={submit}>
        <label htmlFor="submission">What should SiteSense analyze?</label>
        <textarea
          id="submission"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Example: A small clinic website that is difficult to use on mobile..."
          rows={7}
        />
        <button disabled={loading || !input.trim()}>{loading ? "Analyzing..." : "Analyze with Gemma"}</button>
      </form>
      {error && <p role="alert">{error}</p>}
      {selected && (
        <section>
          <h2>Latest analysis</h2>
          <h3>Findings</h3>
          <ul>{parseItems(selected.findings).map((item) => <li key={item}>{item}</li>)}</ul>
          <h3>Recommendations</h3>
          <ul>{parseItems(selected.recommendations).map((item) => <li key={item}>{item}</li>)}</ul>
        </section>
      )}
      <section>
        <h2>History</h2>
        {analyses.length === 0 ? <p>No analyses yet.</p> : analyses.map((analysis) => (
          <button key={analysis.id} type="button" onClick={() => setSelected(analysis)}>
            {analysis.input_text.slice(0, 80)}
          </button>
        ))}
      </section>
    </main>
  );
}
