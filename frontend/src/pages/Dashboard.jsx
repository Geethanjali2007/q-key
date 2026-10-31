import React, { useEffect, useState } from "react";
import { Cpu, ShieldCheck, KeyRound, Lock, RefreshCcw, Activity } from "lucide-react";
import MetricCard from "../components/MetricCard.jsx";
import SecurityBadge from "../components/SecurityBadge.jsx";
import {
  getQRNGStatus,
  getEntropyHealth,
  getKeys,
  getAuditLogs,
} from "../api.js";

export default function Dashboard() {
  const [qrng, setQrng] = useState(null);
  const [entropy, setEntropy] = useState(null);
  const [keys, setKeys] = useState([]);
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState(null);

  async function loadAll() {
    const [q, e, k, l] = await Promise.all([
      getQRNGStatus(),
      getEntropyHealth(),
      getKeys(),
      getAuditLogs(8),
    ]);
    if (q.error) setError(q.error);
    setQrng(q.data);
    setEntropy(e.data);
    setKeys(k.data || []);
    setLogs(l.data || []);
  }

  useEffect(() => {
    loadAll();
    const id = setInterval(loadAll, 10000);
    return () => clearInterval(id);
  }, []);

  const activeKeys = keys.filter((k) => k.status === "ACTIVE").length;
  const fallbackEvents = entropy?.fallback_count ?? 0;
  const encryptionOps = logs.filter((l) => l.event === "ENCRYPTION").length;

  return (
    <div>
      <div className="page-header">
        <h1>Quantum Randomness for Trusted Keys</h1>
        <p className="subtitle">
          Acquire, validate, condition and deliver quantum-generated entropy for cryptographic applications.
        </p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="grid grid-4 section">
        <MetricCard
          icon={Cpu}
          label="Quantum Source"
          value={<SecurityBadge status={qrng?.status || "loading"} />}
          sub={qrng?.provider ? `Provider: ${qrng.provider}` : ""}
        />
        <MetricCard
          icon={ShieldCheck}
          label="Entropy Quality"
          value={entropy?.entropy_quality || "—"}
          sub={entropy ? `Score ${entropy.latest_entropy_score}` : ""}
        />
        <MetricCard icon={KeyRound} label="Active Keys" value={activeKeys} sub={`${keys.length} total generated`} />
        <MetricCard
          icon={RefreshCcw}
          label="Fallback Events"
          value={fallbackEvents}
          sub="CSPRNG used when QRNG unavailable"
        />
      </div>

      <div className="grid grid-2 section">
        <div className="card">
          <div className="card-title" style={{ marginBottom: 14 }}>
            System Snapshot
          </div>
          <table>
            <tbody>
              <tr>
                <td>Tests passed (latest run)</td>
                <td className="mono">{entropy?.tests_passed ?? "—"}</td>
              </tr>
              <tr>
                <td>Tests failed (latest run)</td>
                <td className="mono">{entropy?.tests_failed ?? "—"}</td>
              </tr>
              <tr>
                <td>Total bits generated (session)</td>
                <td className="mono">{entropy?.total_bits_generated ?? "—"}</td>
              </tr>
              <tr>
                <td>Encryption operations (recent)</td>
                <td className="mono">{encryptionOps}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="card">
          <div className="card-title" style={{ marginBottom: 14, display: "flex", alignItems: "center", gap: 8 }}>
            <Activity size={14} /> Recent Activity
          </div>
          <div className="activity-feed">
            {logs.length === 0 && <p>No events recorded yet. Generate a key to get started.</p>}
            {logs.map((log) => (
              <div key={log.id} className="flow-step">
                <div className="step-index mono">{new Date(log.timestamp).toLocaleTimeString()}</div>
                <div>
                  <div className="step-title">{log.event}</div>
                  <div className="step-detail">
                    {log.source} · {log.status}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="note">
        This is a software prototype. Quantum entropy is acquired from an external QRNG provider - no physical
        quantum hardware is contained within this application.
      </div>
    </div>
  );
}
