const API_URL = "http://localhost:8000";

export async function register(data) {
  const response = await fetch(`${API_URL}/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      name: data.name,
      last_name: data.lastName,
      email: data.email,
      password: data.password,
    }),
  });

  if (!response.ok) {
    throw new Error("Registration failed");
  }

  return response.json();
}

export async function login(data) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      
      // get existing users
      const users = JSON.parse(localStorage.getItem("users")) || [];

      // find user with matching credentials from localStorage
      const foundUser = users.find(
        (u) => u.email === data.email && u.password === data.password
      );

      if (foundUser) {
        //login successful → user data
        resolve({
          user: foundUser,
        });
      } else {
        // login failed → error
        reject(new Error("Invalid credentials"));
      }
    }, 500);
  });
}