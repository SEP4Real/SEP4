import { API_URL } from "./apiConfig";

export async function register(data) {
  // send request to backend
  const response = await fetch(`${API_URL}/register`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },

    // send user data
    body: JSON.stringify({
      name: data.name,
      last_name: data.lastName,
      email: data.email,
      password: data.password,
    }),
  });

  // failed -> backend error
  if (!response.ok) {
    const errorData = await response.json();
    console.log(errorData);
    throw new Error(errorData.detail || "Registration failed");
  }

  // success -> backend response
  return response.json();
}

export async function login(data) {
  // send login request to backend
  const response = await fetch(`${API_URL}/login`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },

    // send email and password
    body: JSON.stringify({
      email: data.email,
      password: data.password,
    }),
  });

  // convert response
  const result = await response.json();

  // failed -> error
  if (!response.ok || result.error) {
    throw new Error(result.detail || result.error || "Invalid credentials");
  }
  window.dispatchEvent(new Event("storage"));

  return result;
}

export async function logout() {
  await fetch(`${API_URL}/logout`, {
    method: "POST",
    credentials: "include",
  });
  localStorage.removeItem("user");
  window.dispatchEvent(new Event("storage"));
}

export const connectDevice = (deviceId) => {
  const user = JSON.parse(localStorage.getItem("user"));
  if (!user) return;

  const devices = JSON.parse(localStorage.getItem("user_devices")) || [];

  devices.push({ email: user.email, deviceId: deviceId });
  localStorage.setItem("user_devices", JSON.stringify(devices));
};
