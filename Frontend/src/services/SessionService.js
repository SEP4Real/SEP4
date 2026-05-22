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
