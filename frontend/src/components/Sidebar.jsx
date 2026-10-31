import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Atom,
  Activity,
  GitMerge,
  KeyRound,
  Lock,
  Scale,
  Building2,
  ScrollText,
  HeartPulse,
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/quantum-randomness", label: "Quantum Randomness", icon: Atom },
  { to: "/entropy-analysis", label: "Entropy Analysis", icon: Activity },
  { to: "/entropy-fusion", label: "Entropy Fusion", icon: GitMerge },
  { to: "/key-management", label: "Key Management", icon: KeyRound },
  { to: "/encryption-demo", label: "Encryption Demo", icon: Lock },
  { to: "/qrng-vs-csprng", label: "QRNG vs CSPRNG", icon: Scale },
  { to: "/applications", label: "Applications", icon: Building2 },
  { to: "/audit-logs", label: "Audit Logs", icon: ScrollText },
  { to: "/system-health", label: "System Health", icon: HeartPulse },
];

export default function Sidebar() {
  return (
    <nav
      style={{
        borderRight: "1px solid var(--border)",
        padding: "22px 14px",
        display: "flex",
        flexDirection: "column",
        gap: 2,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "0 10px 22px" }}>
        <div
          style={{
            width: 30,
            height: 30,
            borderRadius: 8,
            background: "var(--accent-soft)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Atom size={17} color="var(--accent)" />
        </div>
        <span style={{ fontFamily: "var(--font-display)", fontWeight: 700, fontSize: 17 }}>Q-Key</span>
      </div>

      {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          style={({ isActive }) => ({
            display: "flex",
            alignItems: "center",
            gap: 10,
            padding: "9px 12px",
            borderRadius: 8,
            fontSize: 13.5,
            fontWeight: 500,
            color: isActive ? "var(--text)" : "var(--text-muted)",
            background: isActive ? "var(--surface-raised)" : "transparent",
            textDecoration: "none",
          })}
        >
          <Icon size={16} />
          {label}
        </NavLink>
      ))}
    </nav>
  );
}
