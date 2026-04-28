import { useState } from "react";
import { register } from "../logic/auth";

// register component
// handles user input and calls register logic
export default function Register({ goToLogin }) {

  // states for form inputs and error message
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState(""); // username used for login (contract)
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  // handle form submission
  const handleSubmit = async (e) => {
    // prevent page reload
    e.preventDefault();

    try {
      // call register function from auth.js
      await register(email, username, password);

      // no error if success
      setError("");

      // redirect to login page registration
      goToLogin();

    } catch (err) {
      // display error message
      setError(err.message);
    }
  };

  return (
    // form triggers handleSubmit on submit
    <form onSubmit={handleSubmit}>
      <h2>Register</h2>

      {/* email input */}
      <input
        type="email"
        placeholder="Email"
        value={email}
        // update email state on change
        onChange={(e) => setEmail(e.target.value)}
      />

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
      <button type="submit">Register</button>

      {/* show error if exists */}
      {error && <p style={{ color: "red" }}>{error}</p>}

      {/* navigation to login page */}
      <p onClick={goToLogin} style={{ cursor: "pointer" }}>
        Already have an account? Login
      </p>
    </form>
  );
}