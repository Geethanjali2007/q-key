import React, { useState } from "react";
import { Landmark, Cpu, Fingerprint } from "lucide-react";
import { runBankingDemo, runIoTDemo, runIdentityDemo } from "../api.js";

function DemoCard({ icon: Icon, title, description, onRun, result, loading }) {
  return (
    <div className="card">
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
        <Icon size={18} color="var(--accent)" />
        <div className="card-title" style={{ marginBottom: 0 }}>{title}</div>
      </div>
      <p style={{ marginBottom: 14 }}>{description}</p>
      <button className="btn btn-primary" onClick={onRun} disabled={loading}>
        {loading ? "Running…" : "Run Demo"}
      </button>

      {result && (
        <div style={{ marginTop: 18 }}>
          {result.steps.map((s, i) => (
            <div className="flow-step" key={i}>
              <div className="step-index mono">{String(i + 1).padStart(2, "0")}</div>
              <div>
                <div className="step-title">{s.step}</div>
                {s.detail && <div className="step-detail mono">{s.detail}</div>}
              </div>
            </div>
          ))}
          <div className="note">{result.note}</div>
        </div>
      )}
    </div>
  );
}

export default function Applications() {
  const [banking, setBanking] = useState(null);
  const [iot, setIot] = useState(null);
  const [identity, setIdentity] = useState(null);
  const [loading, setLoading] = useState({ banking: false, iot: false, identity: false });
  const [error, setError] = useState(null);

  async function run(setter, key, fn) {
    setLoading((l) => ({ ...l, [key]: true }));
    setError(null);
    const { data, error: err } = await fn();
    setLoading((l) => ({ ...l, [key]: false }));
    if (err) {
      setError(err);
      return;
    }
    setter(data);
  }

  return (
    <div>
      <div className="page-header">
        <h1>Applications</h1>
        <p className="subtitle">Simulated integrations showing how real-world systems would request trusted keys.</p>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="grid grid-3">
        <DemoCard
          icon={Landmark}
          title="Banking"
          description="Simulate a bank requesting a quantum-secured session key to protect a transaction."
          onRun={() => run(setBanking, "banking", runBankingDemo)}
          result={banking}
          loading={loading.banking}
        />
        <DemoCard
          icon={Cpu}
          title="IoT Device"
          description="Simulate an IoT sensor registering and establishing a secure communication session."
          onRun={() => run(setIot, "iot", runIoTDemo)}
          result={iot}
          loading={loading.iot}
        />
        <DemoCard
          icon={Fingerprint}
          title="Digital Identity"
          description="Simulate a user login flow that secures a session with quantum-derived key material."
          onRun={() => run(setIdentity, "identity", runIdentityDemo)}
          result={identity}
          loading={loading.identity}
        />
      </div>

      <div className="note">
        These are simulated integrations for demonstration purposes only - no real bank, IoT device, or identity
        provider is contacted.
      </div>
    </div>
  );
}
