import { API_URL } from "./apiConfig";

export async function getDeviceById(deviceId) {
  const response = await fetch(`${API_URL}/device/${encodeURIComponent(deviceId)}`, {
    credentials: "include",
  });

  if (response.status === 404) {
    throw new Error("Device not found. Make sure the physical device is turned on and registered with the backend.");
  }

  if (!response.ok) {
    throw new Error("Could not verify the device with the backend.");
  }

  return response.json();
}

export async function registerDevice(deviceId) {
  const response = await fetch(`${API_URL}/device`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ id: deviceId }),
  });

  if (response.status === 409) {
    return getDeviceById(deviceId);
  }

  if (!response.ok) {
    throw new Error("Could not register the device with the backend.");
  }

  return response.json();
}

export async function ensureDeviceExists(deviceId) {
  try {
    return await getDeviceById(deviceId);
  } catch (error) {
    if (!error.message.startsWith("Device not found")) {
      throw error;
    }

    return registerDevice(deviceId);
  }
}
