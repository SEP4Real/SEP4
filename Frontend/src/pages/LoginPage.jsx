import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login } from "../services/AuthService";
import "./LoginPage.css";

export default function LoginPage() {
  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");

  const navigate = useNavigate();

  function handleChange(e) {
    const { name, value } = e.target;

    setForm({
      ...form,
      [name]: value,
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    if (!form.email || !form.password) {
      setError("Enter email and password");
      return;
    }

    try {
      const result = await login(form);
      localStorage.setItem("user", JSON.stringify(result.user));
      navigate("/student");
    } catch {
      setError("Login failed");
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Hi!</h1>
        <h2>Login</h2>

        <form onSubmit={handleSubmit} className="login-form">
          <label>
            Email:
            <input
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
            />
          </label>

          <label>
            Password:
            <input
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
            />
          </label>

          {error && <p className="login-error">{error}</p>}

          <button type="submit">Login</button>
        </form>

        <p className="auth-link">
          Don’t have an account? <Link to="/register">Register</Link>
        </p>
      </div>
    </div>
  );
}