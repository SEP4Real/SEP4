const MAL_API_URL = import.meta.env.VITE_MAL_API_URL;

export async function getMalHealthCheck() {
  const response = await fetch(`${MAL_API_URL}/`);

  if (!response.ok) {
    throw new Error("MAL backend is not avalable");
  }

  return response.json();
}