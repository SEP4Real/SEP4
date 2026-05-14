const IOT_API_URL = import.meta.env.VITE_IOT_API_URL;

export async function getIoTHealthCheck() {
  const response = await fetch(`${IOT_API_URL}/`);

  if (!response.ok) {
    throw new Error("IoT backend is not available");
  }

  return response.json();
}