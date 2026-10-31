import React, { useState } from "react";
import { GitMerge } from "lucide-react";
import { fuseEntropy } from "../api.js";

export default function EntropyFusion() {
  const [nBytes, setNBytes] = useState(32);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleFuse() {
    setLoading(true);
    setError(null);
    const { data, error: err } = await fuseEntropy(nBytes);
    setLoading(false);
    if (err) {
      setError(err);
      return;
    }
    setResult(data);
  }

  return (
    <div>
      <div className="page-header">
        <h1>Entropy Fusion</h1>
        <p className="subtitle">
          Combine quantum and classical entropy sources into a single output: SHA-256(qrng_bytes || csprng_bytes).
        </p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="grid grid-2 section">
        <div className="card">
          <div className="field">
            <label>Output size (bytes)</label>
            <select value={nBytes} onChange={(e) => setNBytes(Number(e.target.value))}>
              <option value={16}>16</option>
              <option value={32}>32</option>
              <option value={64}>64</option>
            </select>
          </div>
          <button className="btn btn-primary" onClick={handleFuse} disabled={loading}>
            <GitMerge size={16} />
            {loading ? "Fusing sources…" : "Fuse Entropy"}
          </button>

          <div style={{ marginTop: 24 }}>
            <div className="flow-step">
              <div className="step-index mono">1</div>
              <div><div className="step-title">QRNG output</div><div className="step-detail">External quantum entropy source</div></div>
            </div>
            <div className="flow-step">
              <div className="step-index mono">2</div>
              <div><div className="step-title">CSPRNG output</div><div className="step-detail">OS-level cryptographically secure PRNG</div></div>
            </div>
            <div className="flow-step">
              <div className="step-index mono">3</div>
              <div><div className="step-title">SHA-256(quantum || classical)</div><div className="step-detail">Combined, whitened output</div></div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-title">Result</div>
          {!result && !loading && <p style={{ marginTop: 10 }}>No fusion run yet.</p>}
          {loading && <div className="loading-row"><span className="spinner" /> Combining sources…</div>}
          {result && (
            <div style={{ marginTop: 10 }}>
              <div style={{ display: "flex", gap: 10, marginBottom: 14, flexWrap: "wrap" }}>
                <span className={`badge ${result.quantum_source === "available" ? "badge-online" : "badge-offline"}`}>
                  <span className="badge-dot" /> Quantum: {result.quantum_source}
                </span>
                <span className="badge badge-online">
                  <span className="badge-dot" /> Classical: {result.classical_source}
                </span>
              </div>
              <div className="hex-block">{result.output_hex}</div>
              <table style={{ marginTop: 14 }}>
                <tbody>
                  <tr><td>Fusion method</td><td className="mono">{result.fusion_method}</td></tr>
                  <tr><td>Output bits</td><td className="mono">{result.output_bits}</td></tr>
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {result && <div className="note">{result.note}</div>}
    </div>
  );
}
