import React, { useEffect, useState } from "react";
import { RefreshCcw } from "lucide-react";
import { getAuditLogs } from "../api.js";

const STATUS_BADGE = {
  SUCCESS: "badge-online",
  WARNING: "badge-warning",
  FAILURE: "badge-offline",
};

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function load() {
    setLoading(true);
    const { data, error: err } = await getAuditLogs(300);
    setLoading(false);
    if (err) {
      setError(err);
      return;
    }
    setLogs(data || []);
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div>
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
        <div>
          <h1>Audit Logs</h1>
          <p className="subtitle">Security events recorded across the platform.</p>
        </div>
        <button className="btn" onClick={load} disabled={loading}>
          <RefreshCcw size={14} />
          Refresh
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="card">
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Timestamp</th><th>Event</th><th>Source</th><th>Status</th><th>Details</th></tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td className="mono">{new Date(log.timestamp).toLocaleString()}</td>
                  <td>{log.event}</td>
                  <td>{log.source}</td>
                  <td>
                    <span className={`badge ${STATUS_BADGE[log.status] || "badge-neutral"}`}>
                      <span className="badge-dot" />
                      {log.status}
                    </span>
                  </td>
                  <td>{log.details}</td>
                </tr>
              ))}
              {logs.length === 0 && <tr><td colSpan={5}>No audit events recorded yet.</td></tr>}
            </tbody>
          </table>
        </div>
      </div>

      <div className="note">
        Plaintext passwords, secret keys, and authentication tokens are never written to the audit log.
      </div>
    </div>
  );
}
