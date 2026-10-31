import React, { useEffect, useState } from "react";
import { Lock, Unlock } from "lucide-react";
import { getKeys, encryptMessage, decryptMessage } from "../api.js";

export default function EncryptionDemo() {
  const [keys, setKeys] = useState([]);
  const [keyId, setKeyId] = useState("");
  const [plaintext, setPlaintext] = useState("Quantum-secured transaction");
  const [encResult, setEncResult] = useState(null);
  const [decResult, setDecResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    (async () => {
      const { data } = await getKeys();
      const active = (data || []).filter((k) => k.status === "ACTIVE");
      setKeys(active);
      if (active.length) setKeyId(active[0].key_id);
    })();
  }, []);

  async function handleEncrypt() {
    setLoading(true);
    setError(null);
    setDecResult(null);
    const { data, error: err } = await encryptMessage(keyId, plaintext);
    setLoading(false);
    if (err) {
      setError(err);
      return;
    }
    setEncResult(data);
  }

  async function handleDecrypt() {
    if (!encResult) return;
    setLoading(true);
    setError(null);
    const { data, error: err } = await decryptMessage(keyId, encResult.ciphertext, encResult.nonce, encResult.tag);
    setLoading(false);
    if (err) {
      setError(err);
      return;
    }
    setDecResult(data);
  }

  return (
    <div>
      <div className="page-header">
        <h1>Encryption Demo</h1>
        <p className="subtitle">Encrypt and decrypt a message using AES-256-GCM with a trusted key.</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="grid grid-2 section">
        <div className="card">
          <div className="field">
            <label>Active key</label>
            <select value={keyId} onChange={(e) => setKeyId(e.target.value)}>
              {keys.length === 0 && <option value="">No active keys - generate one first</option>}
              {keys.map((k) => (
                <option key={k.key_id} value={k.key_id}>
                  {k.key_id} ({k.source})
                </option>
              ))}
            </select>
          </div>
          <div className="field">
            <label>Plaintext message</label>
            <textarea rows={3} value={plaintext} onChange={(e) => setPlaintext(e.target.value)} />
          </div>
          <button className="btn btn-primary" onClick={handleEncrypt} disabled={!keyId || loading}>
            <Lock size={16} />
            {loading ? "Encrypting…" : "Encrypt"}
          </button>
        </div>

        <div className="card">
          <div className="card-title">Ciphertext</div>
          {!encResult && <p style={{ marginTop: 10 }}>Nothing encrypted yet.</p>}
          {encResult && (
            <div style={{ marginTop: 10 }}>
              <div className="hex-block" style={{ marginBottom: 12 }}>{encResult.ciphertext}</div>
              <table>
                <tbody>
                  <tr><td>Nonce</td><td className="mono">{encResult.nonce}</td></tr>
                  <tr><td>Auth tag</td><td className="mono">{encResult.tag}</td></tr>
                  <tr><td>Algorithm</td><td className="mono">{encResult.algorithm}</td></tr>
                </tbody>
              </table>
              <button className="btn" style={{ marginTop: 14 }} onClick={handleDecrypt} disabled={loading}>
                <Unlock size={16} />
                Decrypt
              </button>
              {decResult && (
                <div style={{ marginTop: 14 }}>
                  <div className="card-title">Decrypted plaintext</div>
                  <div className="hex-block" style={{ color: "var(--text)" }}>{decResult.plaintext}</div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="note">
        A unique 96-bit nonce is generated for every encryption operation. Tampering with the ciphertext or using
        the wrong key causes authentication-tag verification to fail during decryption.
      </div>
    </div>
  );
}
