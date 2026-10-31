import React, { useState } from "react";
import { Scale } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from "recharts";
import { runComparison } from "../api.js";

export default function QRNGvsCSPRNG() {
  const [nBits, setNBits] = useState(100000);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleRun() {
    setLoading(true);
    setError(null);
    const { data, error: err } = await runComparison(nBits);
    setLoading(false);
    if (err) {
      setError(err);
      return;
    }
    setResult(data);
  }

  const latencyData = result
    ? [
        { name: "QRNG", latency: result.qrng.latency_ms || 0 },
        { name: "CSPRNG", latency: result.csprng.latency_ms || 0 },
      ]
    : [];

  const entropyData =
    result && result.qrng.analysis
      ? [
          { name: "QRNG", entropy: result.qrng.analysis.shannon_entropy_bits_per_byte },
          { name: "CSPRNG", entropy: result.csprng.analysis.shannon_entropy_bits_per_byte },
        ]
      : result
      ? [{ name: "CSPRNG", entropy: result.csprng.analysis.shannon_entropy_bits_per_byte }]
      : [];

  return (
    <div>
      <div className="page-header">
        <h1>QRNG vs CSPRNG Laboratory</h1>
        <p className="subtitle">Generate equal amounts of data from both sources and compare statistical quality.</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="card section" style={{ display: "flex", gap: 16, alignItems: "flex-end", flexWrap: "wrap" }}>
        <div className="field" style={{ margin: 0, minWidth: 200 }}>
          <label>Sample size (bits)</label>
          <select value={nBits} onChange={(e) => setNBits(Number(e.target.value))}>
            <option value={8000}>8,000</option>
            <option value={20000}>20,000</option>
            <option value={100000}>100,000</option>
          </select>
        </div>
        <button className="btn btn-primary" onClick={handleRun} disabled={loading}>
          <Scale size={16} />
          {loading ? "Running comparison…" : "Run Comparison"}
        </button>
      </div>

      {result && (
        <>
          <div className="grid grid-2 section">
            {["qrng", "csprng"].map((key) => {
              const src = result[key];
              return (
                <div className="card" key={key}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                    <div className="card-title" style={{ marginBottom: 0 }}>{key.toUpperCase()}</div>
                    <span className={`badge ${src.available ? "badge-online" : "badge-offline"}`}>
                      <span className="badge-dot" />
                      {src.available ? "AVAILABLE" : "UNAVAILABLE"}
                    </span>
                  </div>
                  {src.available ? (
                    <table>
                      <tbody>
                        <tr><td>Latency</td><td className="mono">{src.latency_ms} ms</td></tr>
                        <tr><td>Throughput</td><td className="mono">{src.throughput_bytes_per_sec} B/s</td></tr>
                        <tr><td>Shannon entropy</td><td className="mono">{src.analysis.shannon_entropy_bits_per_byte.toFixed(4)}</td></tr>
                        <tr>
                          <td>Overall quality</td>
                          <td>
                            <span className={`badge ${src.analysis.overall_quality === "Critical" ? "badge-offline" : "badge-online"}`}>
                              <span className="badge-dot" />
                              {src.analysis.overall_quality}
                            </span>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  ) : (
                    <p>{src.error}</p>
                  )}
                </div>
              );
            })}
          </div>

          <div className="grid grid-2 section">
            <div className="card">
              <div className="card-title" style={{ marginBottom: 14 }}>Generation Latency</div>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={latencyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-soft)" />
                  <XAxis dataKey="name" tick={{ fill: "var(--text-muted)" }} />
                  <YAxis tick={{ fill: "var(--text-muted)" }} unit="ms" />
                  <Tooltip contentStyle={{ background: "var(--surface-raised)", border: "1px solid var(--border)" }} />
                  <Bar dataKey="latency" fill="var(--teal)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="card">
              <div className="card-title" style={{ marginBottom: 14 }}>Shannon Entropy (bits/byte)</div>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={entropyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-soft)" />
                  <XAxis dataKey="name" tick={{ fill: "var(--text-muted)" }} />
                  <YAxis domain={[0, 8]} tick={{ fill: "var(--text-muted)" }} />
                  <Tooltip contentStyle={{ background: "var(--surface-raised)", border: "1px solid var(--border)" }} />
                  <Bar dataKey="entropy" fill="var(--accent)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {result.qrng.available && (
            <div className="card section">
              <div className="card-title" style={{ marginBottom: 14 }}>Statistical Test Comparison</div>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr><th>Test</th><th>QRNG</th><th>CSPRNG</th></tr>
                  </thead>
                  <tbody>
                    {result.qrng.analysis.tests.map((t, i) => (
                      <tr key={t.name}>
                        <td>{t.name}</td>
                        <td>
                          <span className={`badge ${t.passed ? "badge-online" : "badge-offline"}`}>
                            <span className="badge-dot" />{t.passed ? "PASS" : "FAIL"}
                          </span>
                        </td>
                        <td>
                          <span className={`badge ${result.csprng.analysis.tests[i].passed ? "badge-online" : "badge-offline"}`}>
                            <span className="badge-dot" />{result.csprng.analysis.tests[i].passed ? "PASS" : "FAIL"}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          <div className="note">{result.note}</div>
        </>
      )}
    </div>
  );
}
