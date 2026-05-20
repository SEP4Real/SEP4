const IOT_API_URL = import.meta.env.VITE_IOT_API_URL;

export async function getIoTHealthCheck() {
  const response = await fetch(`${IOT_API_URL}/`);

  if (!response.ok) {
    throw new Error("IoT backend is not available");
  }

  return response.json();
}

// endpoints based on guessing, maybe theres more, they dont gave swagger enabled 

export async function getSensorData() {
  const response = await fetch(`${IOT_API_URL}/data`);

  if (!response.ok) {
    throw new Error("Failed to fetch sensor data");
  }

  return response.json();
}

export async function getSessions() {
  const response = await fetch(`${IOT_API_URL}/session`);

  if (!response.ok) {
    throw new Error("Failed to fetch sessions");
  }

  return response.json();
}

export async function getDevices() {
  const response = await fetch(`${IOT_API_URL}/device`);

  if (!response.ok) {
    throw new Error("Failed to fetch devices");
  }

  return response.json();
}