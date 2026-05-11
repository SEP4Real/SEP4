import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { register } from "../services/AuthService";
import "../index.css";
import "./RegisterPage.css";
import { useLanguage } from "../context/LanguageContext";

export default function RegisterPage() {
  const [form, setForm] = useState({
    name: "",
    lastName: "",
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const navigate = useNavigate();
   const { t } = useLanguage();

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
      setError(t.fillRequiredFields);
      return;
    }

    try {
      await register(form);
      setSuccess(t.registeredSuccessfully);
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page">
      <div className="card">
        <h1>{t.hi}</h1>
        <h2>{t.registerTitle}</h2>

        <form onSubmit={handleSubmit} className="form">
          <label>
            {t.name}:
            <input name="name" value={form.name} onChange={handleChange} />
          </label>

          <label>
            {t.lastName}:
            <input
              name="lastName"
              value={form.lastName}
              onChange={handleChange}
            />
          </label>

          <label>
            {t.password}:
            <input
              name="password"
              type="password"
              value={form.password}
              onChange={handleChange}
            />
          </label>

          <label>
            {t.email}:
            <input
              name="email"
              type="email"
              value={form.email}
              onChange={handleChange}
            />
          </label>

        
          {error && <p className="error">{error}</p>}
          {success && <p className="success">{success}</p>}

          <button type="submit">{t.register}</button>

          <p className="auth-link">
            {t.alredyHaveAccount} <Link to="/login">{t.login}</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
