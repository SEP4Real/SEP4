import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { login } from "../services/AuthService";
import "./LoginPage.css";
import { useLanguage } from "../context/LanguageContext";

export default function LoginPage() {
  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [error, setError] = useState("");

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

    if (!form.email || !form.password) {
      setError(t.enterEmailPassword);
      return;
    }
    /*const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const result = await login(email, password); 
      if (result.success) {
        navigate("/student");
      }
    } catch (error) {
      alert(error.message); 
    }
    };*/

    try {
      const result = await login(form.email, form.password);
      localStorage.setItem("user", JSON.stringify(result.user));
      window.dispatchEvent(new Event("storage")); 
      navigate("/student");
    } catch {
      setError(t.loginFailed);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>{t.hi}</h1>
        <h2>{t.login}</h2>

        <form onSubmit={handleSubmit} className="login-form">
          <label>
            {t.email}:
            <input
              name="email"
              type="email"
              value={form.email}
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

          {error && <p className="login-error">{error}</p>}

          <button type="submit">{t.login}</button>
        </form>

        <p className="auth-link">
           {t.dontHaveAccount}<Link to="/register">{t.register}</Link>
        </p>
      </div>
    </div>
  );
}