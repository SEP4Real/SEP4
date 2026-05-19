const API_URL = "http://localhost:8080";

export async function submitRating(ratingData) {

  const token = localStorage.getItem("token");

  const response = await fetch(`${API_URL}/ratings`, {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },

    body: JSON.stringify(ratingData),
  });

  if (!response.ok) {
    throw new Error("Failed to submit rating");
  }

  return response.json();
}