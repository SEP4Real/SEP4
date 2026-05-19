const API_URL = "http://localhost:8080";

export async function getDashboardData() {
  const token = localStorage.getItem("token");

  const response = await fetch(`${API_URL}/dashboard`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch dashboard data");
  }

  return response.json();
}