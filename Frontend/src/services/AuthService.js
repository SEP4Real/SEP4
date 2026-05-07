export async function register(data) {
  return new Promise((resolve) => {
    setTimeout(() => {
      // get existing users
      const users = JSON.parse(localStorage.getItem("users")) || [];

      // add user
      users.push(data);

      // save back to localStorage
      localStorage.setItem("users", JSON.stringify(users));

      // simulate success response
      resolve({ ok: true });
    }, 500);
  });
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