import { API_URL } from "./apiConfig";

export async function getProfile() {
  const response = await fetch(`${API_URL}/profile`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch profile");
  }

  return response.json();
}

export async function updateProfile(profileData) {
  const response = await fetch(`${API_URL}/profile`, {
    method: "PUT",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify(profileData),
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

    throw new Error(message || "Failed to update profile");
  }

  return response.json();
}
