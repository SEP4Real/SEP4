import { useState } from "react";
import { login } from "../logic/auth";

// login component
// handles user login and updates app state
export default function Login({ goToRegister, setUser }) {

  // state for form inputs and feedbacks
  const [username, setUsername] = useState(""); 
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // handle form submission
  const handleSubmit = async (e) => {
    // prevent page reload
    e.preventDefault();

    try {
      // call login function from auth.js
      const data = await login(username, password);

      // clear error and set success message
      setError("");
      setSuccess(`Welcome ${data.user.username}!`);

      // store logged-in user in localstorage
      localStorage.setItem("user", data.user.username);

      // store token (used for authenticated API requests later)
      localStorage.setItem("token", data.token);

      // update app state
      setUser(data.user.username);

    } catch (err) {
      // display error message
      setError(err.message);
      setSuccess("");
    }
  };

  return (
    // form triggers handleSubmit on submit
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>

      {/* username input */}
      <input
        type="text"
        placeholder="Username"
        value={username}
        // update username state on change
        onChange={(e) => setUsername(e.target.value)}
      />

      {/* password input */}
      <input
        type="password"
        placeholder="Password"
        value={password}
        // update password state on change
        onChange={(e) => setPassword(e.target.value)}
      />

      {/* submit button */}
      <button type="submit">Login</button>

      {/* show success message if login is successful */}
      {success && <p style={{ color: "green" }}>{success}</p>}

      {/* show error message if login fails */}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {/* navigation to register page */}
      <p onClick={goToRegister} style={{ cursor: "pointer" }}>
        Don't have an account? Register
      </p>
    </form>
  );
}