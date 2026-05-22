import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Eye, EyeOff } from "lucide-react";
import { register, login } from "../services/AuthService";
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
  const [showPassword, setShowPassword] = useState(false);

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

    if (form.password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    if (!/[A-Z]/.test(form.password)) {
      setError("Password must contain an uppercase letter");
      return;
    }

    if (!/[0-9]/.test(form.password)) {
      setError("Password must contain a number");
      return;
    }

    try {
      await register(form);

      const userData = await login({
        email: form.email,
        password: form.password,
      });

      if (!userData.user) {
        throw new Error("Missing login data");
      }

      localStorage.setItem("user", JSON.stringify(userData.user));
      window.dispatchEvent(new Event("storage"));

      setSuccess(t.registeredSuccessfully);

      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="register-page">
      <div className="register-auth-content">
        <h1>{t.hi}</h1>
        <h2>{t.registerTitle}</h2>

        <form onSubmit={handleSubmit} className="register-form">
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
            <div className="auth-password-wrapper">
              <input
                name="password"
                type={showPassword ? "text" : "password"}
                value={form.password}
                onChange={handleChange}
              />
              <button
                type="button"
                className="auth-password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                aria-label={showPassword ? t.hidePassword : t.showPassword}
              >
                {showPassword ? <Eye size={18} /> : <EyeOff size={18} />}
              </button>
            </div>
          </label>

        
          {error && <p className="error">{error}</p>}
          {success && <p className="success">{success}</p>}

          <button type="submit">{t.register}</button>

          <p className="auth-link">
            {t.alreadyHaveAccount} <Link to="/login">{t.goToLogin}</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
