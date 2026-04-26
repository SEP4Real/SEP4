// auth.js = simulates auth -- persist users in localstorage

// load users, if none -> empty array
const users = JSON.parse(localStorage.getItem("users")) || [];

// create a new user with email, username, and password
export const register = async (email, username, password) => { 
  return new Promise((resolve, reject) => {
    // simulate network delay
    setTimeout(() => {
      // does email exist?
      const emailExists = users.find((u) => u.email === email);

      // does username exist?
      const usernameExists = users.find((u) => u.username === username);

      // is email in use? if yes, reject
      if (emailExists) {
        reject(new Error("Email already in use"));
        return;
      }

      // is username in use? if yes, reject
      if (usernameExists) {
        reject(new Error("Username already taken"));
        return;
      }

      // create user
      const newUser = {
        id: users.length + 1,
        username,
        email,
        password,
      };

      // add user to users array
      users.push(newUser);

      // save updated users array to localstorage
      localStorage.setItem("users", JSON.stringify(users));

      // resolve promise to indicate success
      resolve({ message: "User created" });
    }, 500);
  });
};

// login function
// do username and password match a user?
export const login = async (username, password) => {
  return new Promise((resolve, reject) => {
    // simulate network delay
    setTimeout(() => {
      // find user with matching credentials
      const user = users.find(
        (u) => u.username === username && u.password === password
      );

      // match found? if no, reject
      if (!user) {
        reject(new Error("Invalid credentials"));
        return;
      }

      // resolve with fake token and username
      resolve({
        token: "some-token",
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
        },
      });
    }, 500);
  });
};