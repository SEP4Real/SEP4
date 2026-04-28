import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { register } from "../services/authService";
import "../index.css";
import "./RegisterPage.css";

export default function RegisterPage() {
  const [form, setForm] = useState({
    name: "",
    lastName: "",
    email: "",
    password: "",
    studentNumber: "",
    adminNumber: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

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
    setSuccess("");

    if (!form.name || !form.lastName || !form.email || !form.password) {
      setError("Fill required fields");
      return;
    }

    if (!form.studentNumber && !form.adminNumber) {
      setError("Enter student or admin number");
      return;
    }

    if (form.studentNumber && form.adminNumber) {
      setError("Only one: student OR admin");
      return;
    }

    try {
      await register(form);
      setSuccess("Registred successfully");
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page">
      <div className="card">
        <h1>Hi!</h1>
        <h2>Register</h2>

        <form onSubmit={handleSubmit} className="form">
          <label>
            Name:
            <input name="name" value={form.name} onChange={handleChange} />
          </label>

          <label>
            Last name:
            <input
              name="lastName"
              value={form.lastName}
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

          <label>
            Email:
            <input
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
            />
          </label>

          <div className="student-admin-row">
            <label>
              Student nr:
              <input
                name="studentNumber"
                value={form.studentNumber}
                onChange={handleChange}
              />
            </label>

            <span>Or</span>

            <label>
              Admin nr:
              <input
                name="adminNumber"
                value={form.adminNumber}
                onChange={handleChange}
              />
            </label>
          </div>

          {error && <p className="error">{error}</p>}
          {success && <p className="success">{success}</p>}

          <button type="submit">Register</button>

          <p className="auth-link">
            Already have an account? <Link to="/login">Login</Link>
          </p>
        </form>
      </div>
    </div>
  );
}