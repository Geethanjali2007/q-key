import React, { useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { FlaskConical } from "lucide-react";
import { analyzeEntropy } from "../api.js";

export default function EntropyAnalysis() {
  const [source, setSource] = useState("qrng");
  const [nBytes, setNBytes] = useState(256);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleAnalyze() {
    setLoading(true);
    setError(null);
    const { data, error: err } = await analyzeEntropy(source, nBytes);
    setLoading(false);
    if (err) {
      setError(err);
      setResult(null);
      return;
    }
    setResult(data);
  }

  const chartData = result
    ? result.tests.map((t) => ({
        name: t.name.replace(" Test", "").replace(" (m=2)", ""),
        p_value: t.p_value ?? 0,
      }))
    : [];

  return (
    <div>
      <div className="page-header">
        <h1>Entropy Analysis</h1>
        <p className="subtitle">Run statistical randomness tests against a freshly generated entropy sample.</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="card section" style={{ display: "flex", gap: 16, alignItems: "flex-end", flexWrap: "wrap" }}>
        <div className="field" style={{ margin: 0, minWidth: 200 }}>
          <label>Source</label>
          <select value={source} onChange={(e) => setSource(e.target.value)}>
            <option value="qrng">QRNG</option>
            <option value="csprng">CSPRNG</option>
            <option value="fusion">Fusion (QRNG + CSPRNG)</option>
          </select>
        </div>
        <div className="field" style={{ margin: 0, minWidth: 200 }}>
          <label>Sample size (bytes)</label>
          <select value={nBytes} onChange={(e) => setNBytes(Number(e.target.value))}>
            <option value={256}>256</option>
            <option value={1024}>1024</option>
            <option value={4096}>4096</option>
          </select>
        </div>
        <button className="btn btn-primary" onClick={handleAnalyze} disabled={loading}>
          <FlaskConical size={16} />
          {loading ? "Analyzing…" : "Run Analysis"}
        </button>
      </div>

      {result && (
        <>
          <div className="grid grid-4 section">
            <div className="card">
              <div className="card-title">Shannon Entropy</div>
              <div className="card-value">{result.shannon_entropy_bits_per_byte.toFixed(3)} <span style={{fontSize: 14, color: "var(--text-muted)"}}>bits/byte</span></div>
            </div>
            <div className="card">
              <div className="card-title">Min-Entropy</div>
              <div className="card-value">{result.min_entropy_bits_per_byte.toFixed(3)}</div>
            </div>
            <div className="card">
              <div className="card-title">Ones / Zeros Ratio</div>
              <div className="card-value">{(result.ones_ratio * 100).toFixed(1)}% / {(result.zeros_ratio * 100).toFixed(1)}%</div>
            </div>
            <div className="card">
              <div className="card-title">Overall Quality</div>
              <div className="card-value">{result.overall_quality}</div>
            </div>
          </div>

          <div className="card section">
            <div className="card-title" style={{ marginBottom: 14 }}>Test p-values</div>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-soft)" />
                <XAxis dataKey="name" tick={{ fill: "var(--text-muted)", fontSize: 11 }} interval={0} angle={-15} textAnchor="end" height={60} />
                <YAxis domain={[0, 1]} tick={{ fill: "var(--text-muted)", fontSize: 11 }} />
                <Tooltip contentStyle={{ background: "var(--surface-raised)", border: "1px solid var(--border)" }} />
                <Bar dataKey="p_value" fill="var(--accent)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="card section">
            <div className="card-title" style={{ marginBottom: 14 }}>Detailed Results</div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr><th>Test</th><th>Statistic</th><th>p-value</th><th>Threshold</th><th>Result</th></tr>
                </thead>
                <tbody>
                  {result.tests.map((t) => (
                    <tr key={t.name}>
                      <td>{t.name}</td>
                      <td className="mono">{t.statistic}</td>
                      <td className="mono">{t.p_value ?? "—"}</td>
                      <td className="mono">{t.threshold}</td>
                      <td>
                        <span className={`badge ${t.passed ? "badge-online" : "badge-offline"}`}>
                          <span className="badge-dot" />
                          {t.passed ? "PASS" : "FAIL"}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="note">{result.note}</div>
        </>
      )}
    </div>
  );
}
