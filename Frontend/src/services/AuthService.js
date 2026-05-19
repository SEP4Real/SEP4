const API_URL = "http://localhost:8080";

/* export async function register(data) {
  // send request to backend
  const response = await fetch(`${API_URL}/register`, {
    method: "POST",
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
} */

  export async function register(data) {
  console.log("Simulare înregistrare directă...");
  
  localStorage.setItem("user", JSON.stringify({ email: data.email, name: data.name }));
  localStorage.setItem("jwt", "mock-token-prezentare-rapida"); 

  window.dispatchEvent(new Event("storage"));

  return { message: "Success" };
}

export async function login(data) {
  // send login request to backend
  const response = await fetch(`${API_URL}/login`, {
    method: "POST",
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
    throw new Error(result.error || "Invalid credentials");
  }
  localStorage.setItem("user", JSON.stringify({ email: data.email }));
  localStorage.setItem("jwt", result.token || "mock-token-autentificare");
  window.dispatchEvent(new Event("storage"));

  return result;
}

export function logout() {
  localStorage.removeItem("user");
  localStorage.removeItem('jwt');
  window.dispatchEvent(new Event("storage"));
}

export const connectDevice = (deviceId) => {
  const user = JSON.parse(localStorage.getItem("user"));
  if (!user) return;

  const devices = JSON.parse(localStorage.getItem("user_devices")) || [];

  devices.push({ email: user.email, deviceId: deviceId });
  localStorage.setItem("user_devices", JSON.stringify(devices));
};
