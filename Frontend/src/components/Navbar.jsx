import { useState } from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';
import { useTheme } from "../context/ThemeContext";

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const { theme, toggleTheme } = useTheme();

  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <span className="logo-icon">🌿</span> Student Environment Helper
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
          <Link to="/" onClick={() => setIsMenuOpen(false)}>Register</Link>
        </li>
        <li>
          <Link to="/history" onClick={() => setIsMenuOpen(false)}>History</Link>
        </li>
        <li>
          <Link to="/student" onClick={() => setIsMenuOpen(false)}> Dashboard</Link>
        </li>
        <li>
                <Link to="/profile" onClick={() => setIsMenuOpen(false)}> Profile</Link>
        </li>
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
      </ul>
    </nav>
  );
};

export default Navbar;
