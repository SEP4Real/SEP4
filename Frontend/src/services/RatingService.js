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
    throw new Error("Failed to submit rating");
  }

  return response.json();
}
