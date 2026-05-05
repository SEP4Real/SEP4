import { Link } from 'react-router-dom';
import './Navbar.css';
import { useState, useEffect } from 'react';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  

  const [user, setUser] = useState(localStorage.getItem("user"));

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

      {/* not logged in*/}
      {!user && (
        <>
          <li>
            <Link to="/register" onClick={() => setIsMenuOpen(false)}>Register</Link>
          </li>
          <li>
            <Link to="/login" onClick={() => setIsMenuOpen(false)}>Login</Link>
          </li>
        </>
      )}

      {/* logged in */}
      {user && (
        <>
          <li>
            <Link to="/calendar" onClick={() => setIsMenuOpen(false)}>Calendar</Link>
          </li>
          <li>
            <Link to="/history" onClick={() => setIsMenuOpen(false)}>History</Link>
          </li>
          <li>
            <Link to="/student" onClick={() => setIsMenuOpen(false)}>Dashboard</Link>
          </li>
          <li>
            <Link to="/profile" onClick={() => setIsMenuOpen(false)}>Profile</Link>
          </li>
        </>
      )}

    </ul>
    </nav>
  );
};

export default Navbar;
