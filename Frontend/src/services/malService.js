const MAL_API_URL = "http://localhost:8000";

export async function getMalHealthCheck() {
  const response = await fetch(`${MAL_API_URL}/`);

  if (!response.ok) {
    throw new Error("MAL backend is not avalable");
  }

  return response.json();
}