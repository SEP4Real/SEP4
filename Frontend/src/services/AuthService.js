export async function register(data) {
  console.log("Sending to backend:", data);

  return new Promise((resolve) => {
    setTimeout(() => {
      const users = JSON.parse(localStorage.getItem("users")) || [];

      if (!users.find(u => u.email === data.email)) {
        users.push(data);
        localStorage.setItem("users", JSON.stringify(users));
      } //check if the user exists

      const userData = {
        email: data.email,
        name: data.name,
        lastName: data.lastName,
        role: "Student" 
      };
      localStorage.setItem('user', JSON.stringify(userData));
      resolve({ ok: true, user: userData });
    }, 500);
  });
}

export async function login(data) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const allUsers = JSON.parse(localStorage.getItem("users")) || [];
      const foundUser = allUsers.find(
        (u) => u.email === data.email && u.password === data.password
      );

      if (foundUser) {
        localStorage.setItem('user', JSON.stringify(foundUser));
        resolve({ user: foundUser });
      } else {
        reject(new Error("Invalid email or password"));
      }
    }, 500);
  });
}
       // Store user info in local storage to maintain the session and 
       // provide data to the Profile page
        