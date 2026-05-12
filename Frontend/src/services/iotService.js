const IOT_API_URL = "http://localhost:8080";

export async function getIoTHealthCheck() {
  const response = await fetch(`${IOT_API_URL}/`);

  if (!response.ok) {
    throw new Error("IoT backend is not available");
  }

  return response.json();
}