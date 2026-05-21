import { API_URL } from "./apiConfig";

export async function getDashboardData() {
  const response = await fetch(`${API_URL}/dashboard`, {
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch dashboard data");
  }

  return response.json();
}
