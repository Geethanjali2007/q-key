/**
 * Central API client for the Q-Key backend.
 *
 * Every function returns { data, error }. Callers should check `error`
 * before using `data`. This module never throws for expected failure
 * modes (backend down, timeout, non-2xx response) - it always resolves.
 */
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const DEFAULT_TIMEOUT_MS = 12000;

async function request(path, options = {}) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);

  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json" },
      signal: controller.signal,
      ...options,
    });

    clearTimeout(timeout);

    let body = null;
    try {
      body = await res.json();
    } catch {
      body = null;
    }

    if (!res.ok) {
      const message = (body && body.detail) || `Request failed with status ${res.status}`;
      return { data: null, error: message };
    }

    return { data: body, error: null };
  } catch (err) {
    clearTimeout(timeout);
    if (err.name === "AbortError") {
      return { data: null, error: "Request timed out. Is the backend running?" };
    }
    return { data: null, error: "Could not reach the Q-Key backend. Is it running on " + BASE_URL + "?" };
  }
}

// --- System / health ---
export const getSystemHealth = () => request("/health");
export const getQRNGStatus = () => request("/qrng/status");
export const getEntropyHealth = () => request("/entropy/health");

// --- Randomness ---
export const generateRandom = (n_bytes = 32, source = "qrng") =>
  request("/qrng/random", { method: "POST", body: JSON.stringify({ n_bytes, source }) });

// --- Entropy analysis / fusion ---
export const analyzeEntropy = (source = "qrng", n_bytes = 256) =>
  request("/entropy/analyze", { method: "POST", body: JSON.stringify({ source, n_bytes }) });

export const fuseEntropy = (n_bytes = 32) =>
  request("/entropy/fuse", { method: "POST", body: JSON.stringify({ n_bytes }) });

// --- Key management ---
export const generateKey = (source = "qrng", algorithm = "AES-256-GCM", label = null) =>
  request("/keys/generate", { method: "POST", body: JSON.stringify({ source, algorithm, label }) });

export const getKeys = () => request("/keys");
export const getKey = (keyId) => request(`/keys/${keyId}`);
export const rotateKey = (keyId) => request(`/keys/${keyId}/rotate`, { method: "POST" });
export const revokeKey = (keyId) => request(`/keys/${keyId}/revoke`, { method: "POST" });

// --- Encryption ---
export const encryptMessage = (key_id, plaintext) =>
  request("/crypto/encrypt", { method: "POST", body: JSON.stringify({ key_id, plaintext }) });

export const decryptMessage = (key_id, ciphertext, nonce, tag) =>
  request("/crypto/decrypt", { method: "POST", body: JSON.stringify({ key_id, ciphertext, nonce, tag }) });

// --- Audit ---
export const getAuditLogs = (limit = 200) => request(`/audit/logs?limit=${limit}`);

// --- Applications ---
export const getApplicationStatus = () => request("/applications/status");
export const runBankingDemo = () => request("/applications/banking/demo", { method: "POST" });
export const runIoTDemo = () => request("/applications/iot/demo", { method: "POST" });
export const runIdentityDemo = () => request("/applications/identity/demo", { method: "POST" });

// --- Comparison lab ---
export const runComparison = (n_bits = 100000) => request(`/comparison/qrng-csprng?n_bits=${n_bits}`);
