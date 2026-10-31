import React, { useEffect, useState } from "react";
import { KeyRound, RotateCw, Ban } from "lucide-react";
import { generateKey, getKeys, rotateKey, revokeKey } from "../api.js";

const STATUS_BADGE = {
  ACTIVE: "badge-online",
  ROTATED: "badge-neutral",
  REVOKED: "badge-offline",
  EXPIRED: "badge-warning",
};

export default function KeyManagement() {
  const [keys, setKeys] = useState([]);
  const [source, setSource] = useState("qrng");
  const [label, setLabel] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [busyId, setBusyId] = useState(null);

  async function loadKeys() {
    const { data, error: err } = await getKeys();
    if (err) setError(err);
    setKeys(data || []);
  }

  useEffect(() => {
    loadKeys();
  }, []);

  async function handleGenerate() {
    setLoading(true);
    setError(null);
    const { error: err } = await generateKey(source, "AES-256-GCM", label || null);
    setLoading(false);
    if (err) {
      setError(err);
      return;
    }
    setLabel("");
    loadKeys();
  }

  async function handleRotate(keyId) {
    setBusyId(keyId);
    const { error: err } = await rotateKey(keyId);
    setBusyId(null);
    if (err) setError(err);
    loadKeys();
  }

  async function handleRevoke(keyId) {
    setBusyId(keyId);
    const { error: err } = await revokeKey(keyId);
    setBusyId(null);
    if (err) setError(err);
    loadKeys();
  }

  return (
    <div>
      <div className="page-header">
        <h1>Key Management</h1>
        <p className="subtitle">Generate, rotate, and revoke AES-256-GCM keys sourced from trusted entropy.</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="card section" style={{ display: "flex", gap: 16, alignItems: "flex-end", flexWrap: "wrap" }}>
        <div className="field" style={{ margin: 0, minWidth: 200 }}>
          <label>Entropy source</label>
          <select value={source} onChange={(e) => setSource(e.target.value)}>
            <option value="qrng">QRNG</option>
            <option value="csprng">CSPRNG</option>
            <option value="fusion">Fusion</option>
          </select>
        </div>
        <div className="field" style={{ margin: 0, minWidth: 240, flex: 1 }}>
          <label>Label (optional)</label>
          <input value={label} onChange={(e) => setLabel(e.target.value)} placeholder="e.g. banking-session-key" />
        </div>
        <button className="btn btn-primary" onClick={handleGenerate} disabled={loading}>
          <KeyRound size={16} />
          {loading ? "Generating…" : "Generate Key"}
        </button>
      </div>

      <div className="card">
        <div className="card-title" style={{ marginBottom: 14 }}>Keys ({keys.length})</div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Key ID</th>
                <th>Algorithm</th>
                <th>Version</th>
                <th>Source</th>
                <th>Status</th>
                <th>Created</th>
                <th>Preview</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {keys.map((k) => (
                <tr key={k.key_id}>
                  <td className="mono">{k.key_id}</td>
                  <td>{k.algorithm}</td>
                  <td>{k.key_version}</td>
                  <td>{k.source}</td>
                  <td>
                    <span className={`badge ${STATUS_BADGE[k.status] || "badge-neutral"}`}>
                      <span className="badge-dot" />
                      {k.status}
                    </span>
                  </td>
                  <td>{new Date(k.created_at).toLocaleString()}</td>
                  <td className="mono">{k.demo_preview || "hidden"}</td>
                  <td style={{ display: "flex", gap: 6 }}>
                    <button
                      className="btn"
                      style={{ padding: "6px 10px" }}
                      onClick={() => handleRotate(k.key_id)}
                      disabled={k.status !== "ACTIVE" || busyId === k.key_id}
                    >
                      <RotateCw size={13} />
                    </button>
                    <button
                      className="btn btn-danger"
                      style={{ padding: "6px 10px" }}
                      onClick={() => handleRevoke(k.key_id)}
                      disabled={k.status === "REVOKED" || busyId === k.key_id}
                    >
                      <Ban size={13} />
                    </button>
                  </td>
                </tr>
              ))}
              {keys.length === 0 && (
                <tr><td colSpan={8}>No keys generated yet.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="note">
        Secret key material is never exposed by the API. The "Preview" column shows a masked representation only
        because DEMO_MODE is enabled for this hackathon prototype.
      </div>
    </div>
  );
}
