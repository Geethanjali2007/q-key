import React from "react";

const CONFIG = {
  ONLINE: { cls: "badge-online", label: "QRNG Online" },
  OFFLINE: { cls: "badge-offline", label: "QRNG Offline" },
  DEGRADED: { cls: "badge-warning", label: "Degraded Mode" },
  loading: { cls: "badge-neutral", label: "Checking status…" },
};

export default function SecurityBadge({ status }) {
  const config = CONFIG[status] || CONFIG.loading;
  return (
    <span className={`badge ${config.cls}`}>
      <span className="badge-dot" />
      {config.label}
    </span>
  );
}
