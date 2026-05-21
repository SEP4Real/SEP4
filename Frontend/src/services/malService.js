const MAL_API_URL = import.meta.env.VITE_MAL_API_URL;

export async function getMalHealthCheck() {
  const response = await fetch(`${MAL_API_URL}/`);

  if (!response.ok) {
    throw new Error("MAL backend is not avalable");
  }

  return response.json();
}

export async function getPrediction(data) {
  const response = await fetch(`${MAL_API_URL}/predict`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error("Prediction request failed");
  }

  return response.json();
}