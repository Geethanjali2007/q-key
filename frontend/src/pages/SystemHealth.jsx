import React, { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import SecurityBadge from "../components/SecurityBadge.jsx";
import { getQRNGStatus, getEntropyHealth } from "../api.js";

export default function SystemHealth() {
  const [qrng, setQrng] = useState(null);
  const [entropy, setEntropy] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);

  async function poll() {
    const [q, e] = await Promise.all([getQRNGStatus(), getEntropyHealth()]);
    if (q.error) setError(q.error);
    setQrng(q.data);
    setEntropy(e.data);
    if (e.data) {
      setHistory((h) =>
        [...h, { time: new Date().toLocaleTimeString(), score: e.data.latest_entropy_score }].slice(-20)
      );
    }
  }

  useEffect(() => {
    poll();
    const id = setInterval(poll, 8000);
    return () => clearInterval(id);
  }, []);

  return (
    <div>
      <div className="page-header">
        <h1>System Health</h1>
        <p className="subtitle">Continuous monitoring of the entropy source and platform status.</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="grid grid-4 section">
        <div className="card">
          <div className="card-title">QRNG Source</div>
          <div style={{ marginTop: 10 }}>
            <SecurityBadge status={qrng?.status || "loading"} />
          </div>
        </div>
        <div className="card">
          <div className="card-title">Entropy Quality</div>
          <div className="card-value">{entropy?.entropy_quality ?? "—"}</div>
        </div>
        <div className="card">
          <div className="card-title">Failed Requests</div>
          <div className="card-value">{qrng?.failed_requests ?? 0}</div>
        </div>
        <div className="card">
          <div className="card-title">Fallback Count</div>
          <div className="card-value">{entropy?.fallback_count ?? 0}</div>
        </div>
      </div>

      <div className="card section">
        <div className="card-title" style={{ marginBottom: 14 }}>Entropy Score Over Time</div>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={history}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-soft)" />
            <XAxis dataKey="time" tick={{ fill: "var(--text-muted)", fontSize: 11 }} />
            <YAxis domain={[0, 1]} tick={{ fill: "var(--text-muted)", fontSize: 11 }} />
            <Tooltip contentStyle={{ background: "var(--surface-raised)", border: "1px solid var(--border)" }} />
            <Line type="monotone" dataKey="score" stroke="var(--accent)" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <div className="card-title" style={{ marginBottom: 14 }}>Request Statistics</div>
          <table>
            <tbody>
              <tr><td>Total requests</td><td className="mono">{qrng?.total_requests ?? 0}</td></tr>
              <tr><td>Failed requests</td><td className="mono">{qrng?.failed_requests ?? 0}</td></tr>
              <tr><td>Last success</td><td className="mono">{qrng?.last_success || "—"}</td></tr>
              <tr><td>Last failure</td><td className="mono">{qrng?.last_failure || "—"}</td></tr>
              <tr><td>Fallback allowed</td><td className="mono">{String(qrng?.allow_fallback)}</td></tr>
            </tbody>
          </table>
        </div>
        <div className="card">
          <div className="card-title" style={{ marginBottom: 14 }}>Statistical Test Summary</div>
          <table>
            <tbody>
              <tr><td>Tests passed (latest)</td><td className="mono">{entropy?.tests_passed ?? "—"}</td></tr>
              <tr><td>Tests failed (latest)</td><td className="mono">{entropy?.tests_failed ?? "—"}</td></tr>
              <tr><td>Total bits generated</td><td className="mono">{entropy?.total_bits_generated ?? "—"}</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="note">
        This health score is a transparent operational heuristic for monitoring purposes. It is not a formal
        cryptographic security proof.
      </div>
    </div>
  );
}
