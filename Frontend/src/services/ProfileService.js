import { apiFetch } from "./apiConfig";

export async function getProfile() {
  const response = await apiFetch("/profile");

  if (!response.ok) {
    throw new Error("Failed to fetch profile");
  }

  return response.json();
}

export async function updateProfile(profileData) {
  const response = await apiFetch("/profile", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify(profileData),
  });

  if (!response.ok) {
    throw new Error("Failed to update profile");
  }

  return response.json();
}
