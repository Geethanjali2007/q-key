import React, { useState } from "react";
import { Dices } from "lucide-react";
import SecurityBadge from "../components/SecurityBadge.jsx";
import { generateRandom } from "../api.js";

const SIZES = [16, 32, 64, 128];

export default function QuantumRandomness() {
  const [nBytes, setNBytes] = useState(32);
  const [source, setSource] = useState("qrng");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    const { data, error: err } = await generateRandom(nBytes, source);
    setLoading(false);
    if (err) {
      setError(err);
      setResult(null);
      return;
    }
    setResult(data);
  }

  return (
    <div>
      <div className="page-header">
        <h1>Quantum Randomness</h1>
        <p className="subtitle">Request raw entropy directly from the external QRNG provider or the OS CSPRNG.</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="grid grid-2 section">
        <div className="card">
          <div className="field">
            <label>Source</label>
            <select value={source} onChange={(e) => setSource(e.target.value)}>
              <option value="qrng">QRNG (external quantum source)</option>
              <option value="csprng">CSPRNG (OS secrets module)</option>
            </select>
          </div>
          <div className="field">
            <label>Number of bytes</label>
            <select value={nBytes} onChange={(e) => setNBytes(Number(e.target.value))}>
              {SIZES.map((s) => (
                <option key={s} value={s}>
                  {s} bytes ({s * 8} bits)
                </option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary" onClick={handleGenerate} disabled={loading}>
            <Dices size={16} />
            {loading ? "Requesting entropy…" : "Generate Random Data"}
          </button>
        </div>

        <div className="card">
          <div className="card-title">Result</div>
          {!result && !loading && <p style={{ marginTop: 10 }}>No data generated yet.</p>}
          {loading && <div className="loading-row"><span className="spinner" /> Contacting entropy source…</div>}
          {result && (
            <div style={{ marginTop: 10 }}>
              <div style={{ display: "flex", gap: 10, marginBottom: 14, flexWrap: "wrap" }}>
                <span className="badge badge-neutral">{result.source}</span>
                {result.provider && <span className="badge badge-neutral">{result.provider}</span>}
                {result.fallback_used && <SecurityBadge status="DEGRADED" />}
              </div>
              <div className="hex-block">{result.hex}</div>
              <table style={{ marginTop: 14 }}>
                <tbody>
                  <tr><td>Bytes</td><td className="mono">{result.bytes}</td></tr>
                  <tr><td>Bits</td><td className="mono">{result.bits}</td></tr>
                  <tr><td>Request ID</td><td className="mono">{result.request_id}</td></tr>
                  <tr><td>Timestamp</td><td className="mono">{result.timestamp}</td></tr>
                </tbody>
              </table>
              {result.warning && <div className="note">{result.warning}</div>}
            </div>
          )}
        </div>
      </div>

      <div className="note">
        QRNG data is sourced from an external provider that derives randomness from physical quantum measurement.
        CSPRNG data is generated locally using Python's cryptographically secure "secrets" module - it is
        computationally secure, not "insecure" or "broken".
      </div>
    </div>
  );
}
