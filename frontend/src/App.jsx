import React from "react";
import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar.jsx";
import Navbar from "./components/Navbar.jsx";

import Dashboard from "./pages/Dashboard.jsx";
import QuantumRandomness from "./pages/QuantumRandomness.jsx";
import EntropyAnalysis from "./pages/EntropyAnalysis.jsx";
import EntropyFusion from "./pages/EntropyFusion.jsx";
import KeyManagement from "./pages/KeyManagement.jsx";
import EncryptionDemo from "./pages/EncryptionDemo.jsx";
import QRNGvsCSPRNG from "./pages/QRNGvsCSPRNG.jsx";
import Applications from "./pages/Applications.jsx";
import AuditLogs from "./pages/AuditLogs.jsx";
import SystemHealth from "./pages/SystemHealth.jsx";

export default function App() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-main">
        <Navbar />
        <div className="page-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/quantum-randomness" element={<QuantumRandomness />} />
            <Route path="/entropy-analysis" element={<EntropyAnalysis />} />
            <Route path="/entropy-fusion" element={<EntropyFusion />} />
            <Route path="/key-management" element={<KeyManagement />} />
            <Route path="/encryption-demo" element={<EncryptionDemo />} />
            <Route path="/qrng-vs-csprng" element={<QRNGvsCSPRNG />} />
            <Route path="/applications" element={<Applications />} />
            <Route path="/audit-logs" element={<AuditLogs />} />
            <Route path="/system-health" element={<SystemHealth />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}
