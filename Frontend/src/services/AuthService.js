export const register = async (userData) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // save the received data in localStorage under the key "user"
      const allUsers = JSON.parse(localStorage.getItem("users")) || [];
      allUsers.push(userData);
      localStorage.setItem("users", JSON.stringify(allUsers));

      localStorage.setItem("user", JSON.stringify(userData));
      resolve({ success: true, user: userData });
    }, 500);
  });
};

export const login = async (email, password) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const rawData = localStorage.getItem("users");
      let allUsers = [];

      try {
        const parsedData = JSON.parse(rawData);
        // Forțăm allUsers să fie un array, chiar dacă datele sunt corupte
        allUsers = Array.isArray(parsedData) ? parsedData : [];
      } catch (e) {
        allUsers = [];
      }

      const foundUser = allUsers.find(
        (u) => u.email === email && String(u.password) === String(password)
      );

      if (foundUser) {
        localStorage.setItem("user", JSON.stringify(foundUser));
        resolve({ success: true, user: foundUser });
      } else {
        reject(new Error("Invalid email or password"));
      }
    }, 500);
  });
};


export function logout() {
  localStorage.removeItem('user');
  window.dispatchEvent(new Event("storage"));
}
