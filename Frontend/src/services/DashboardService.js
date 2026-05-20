import { apiFetch } from "./apiConfig";

export async function getDashboardData() {
  const response = await apiFetch("/dashboard");

  if (!response.ok) {
    throw new Error("Failed to fetch dashboard data");
  }

  return response.json();
}
