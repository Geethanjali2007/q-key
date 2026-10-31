import React, { useEffect, useState } from "react";
import { Atom } from "lucide-react";
import SecurityBadge from "./SecurityBadge.jsx";
import { getQRNGStatus } from "../api.js";

export default function Navbar() {
  const [status, setStatus] = useState(null);

  useEffect(() => {
    let mounted = true;
    async function poll() {
      const { data } = await getQRNGStatus();
      if (mounted && data) setStatus(data.status);
    }
    poll();
    const id = setInterval(poll, 15000);
    return () => {
      mounted = false;
      clearInterval(id);
    };
  }, []);

  return (
    <header
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "16px 32px",
        borderBottom: "1px solid var(--border)",
        background: "rgba(10,12,18,0.7)",
        backdropFilter: "blur(6px)",
        position: "sticky",
        top: 0,
        zIndex: 10,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <Atom size={18} color="var(--accent)" />
        <span style={{ fontFamily: "var(--font-display)", fontSize: 14, color: "var(--text-muted)" }}>
          Quantum Randomness Security Platform
        </span>
      </div>
      <SecurityBadge status={status || "loading"} />
    </header>
  );
}
