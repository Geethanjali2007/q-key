import React from "react";

export default function MetricCard({ icon: Icon, label, value, sub }) {
  return (
    <div className="card">
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div className="card-title" style={{ marginBottom: 0 }}>
          {label}
        </div>
        {Icon && <Icon size={16} color="var(--text-faint)" />}
      </div>
      <div className="card-value" style={{ marginTop: 10 }}>
        {value}
      </div>
      {sub && <p style={{ marginTop: 6, fontSize: 12.5 }}>{sub}</p>}
    </div>
  );
}
