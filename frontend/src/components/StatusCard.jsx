import React from "react";

/**
 * A card summarizing a source/system status with a colored indicator.
 * tone: "good" | "bad" | "warn" | "neutral"
 */
const TONE_COLORS = {
  good: "var(--teal)",
  bad: "var(--red)",
  warn: "var(--amber)",
  neutral: "var(--text-muted)",
};

export default function StatusCard({ title, value, tone = "neutral", detail }) {
  return (
    <div className="card">
      <div className="card-title">{title}</div>
      <div className="card-value" style={{ color: TONE_COLORS[tone] }}>
        {value}
      </div>
      {detail && <p style={{ marginTop: 8, fontSize: 13 }}>{detail}</p>}
    </div>
  );
}
