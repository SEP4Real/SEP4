import { API_URL } from "./apiConfig";

export async function getDeviceSessions(deviceId) {
  const response = await fetch(`${API_URL}/session/device/${deviceId}`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch device sessions");
  }

  return response.json();
}

export async function getCurrentSession(deviceId) {
  const query = deviceId ? `?deviceId=${encodeURIComponent(deviceId)}` : "";
  const response = await fetch(`${API_URL}/session/current${query}`, {
    credentials: "include",
  });

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error("Failed to fetch active session");
  }

  return response.json();
}
