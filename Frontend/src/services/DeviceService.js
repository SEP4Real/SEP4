const API_URL = "http://localhost:8080";

export async function getDeviceById(deviceId) {
  const response = await fetch(`${API_URL}/device/${encodeURIComponent(deviceId)}`);

  if (response.status === 404) {
    throw new Error("Device not found in the database.");
  }

  if (!response.ok) {
    throw new Error("Could not verify the device with the backend.");
  }

  return response.json();
}
