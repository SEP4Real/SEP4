import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';
import { useTheme } from "../context/ThemeContext";
import { useLanguage } from "../context/LanguageContext";
import { useState, useEffect } from 'react';


const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [user, setUser] = useState(localStorage.getItem("user"));
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const { language, toggleLanguage, t } = useLanguage();
 

  useEffect(() => {
    const handleStorageChange = () => {
      setUser(localStorage.getItem("user"));
    };

    window.addEventListener("storage", handleStorageChange);
    setUser(localStorage.getItem("user"));

    return () => {
      window.removeEventListener("storage", handleStorageChange);
    };

  }, []);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <span className="logo-icon">🌿</span> {t.appName}
      </div>

      {/*Hamburger  Buton  */}
      <div className={`hamburger ${isMenuOpen ? 'open' : ''}`} onClick={toggleMenu}>
        <div className="bar"></div>
        <div className="bar"></div>
        <div className="bar"></div>
      </div>

      {/* Link */}
      <ul className={`nav-links ${isMenuOpen ? 'show' : ''}`}>
        <li>
          <span
            className="theme-icon-button"
            onClick={toggleTheme}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                toggleTheme();
              }
            }}
          >
            {theme === "light" ? "⋆☾˚" : "🔆"}
          </span>
        </li>

        <li>
          <span
            className="language-toggle"
            onClick={toggleLanguage}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                toggleLanguage();
              }
            }}
          >
            {language === "en" ? "DK" : "EN"}
          </span>
        </li>

        {!user && (
          <>
            {location.pathname !== "/register" && (
              <li>
                <Link to="/register" onClick={() => setIsMenuOpen(false)}>
                  Register
                </Link>
              </li>
            )}

            {location.pathname !== "/login" && (
              <li>
                <Link to="/login" onClick={() => setIsMenuOpen(false)}>
                  Login
                </Link>
              </li>
            )}
          </>
        )}

        {user && (
          <>
            <li>
              <Link to="/calendar" onClick={() => setIsMenuOpen(false)}>
                Calendar
              </Link>
            </li>

            <li>
              <Link to="/history" onClick={() => setIsMenuOpen(false)}>
                History
              </Link>
            </li>

            <li>
              <Link to="/dashboard" onClick={() => setIsMenuOpen(false)}>
                Dashboard
              </Link>
            </li>

            <li>
              <Link to="/profile" onClick={() => setIsMenuOpen(false)}>
                Profile
              </Link>
            </li>
          </>
        )}
      </ul>
    </nav>
  );
};

export default Navbar;
