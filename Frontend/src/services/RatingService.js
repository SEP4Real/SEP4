import { API_URL } from "./apiConfig";

export async function submitRating(ratingData) {
  const response = await fetch(`${API_URL}/ratings`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(ratingData),
  });

  if (!response.ok) {
    const errorText = await response.text();
    let message = errorText;

    try {
      const error = JSON.parse(errorText);
      message = error?.detail || message;
    } catch {
      message = errorText;
    }

    throw new Error(message || "Failed to submit rating");
  }

  return response.json();
}
