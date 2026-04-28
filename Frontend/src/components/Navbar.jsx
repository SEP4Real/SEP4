import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Navbar.css';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

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
        <li>
          <Link to="/" onClick={() => setIsMenuOpen(false)}>Register</Link>
        </li>
        <li>
          <Link to="/history" onClick={() => setIsMenuOpen(false)}>History</Link>
        </li>
        <li>
          <Link to="/student" onClick={() => setIsMenuOpen(false)}>Student Dashboard</Link>
        </li>
        <li>
          <Link to="/admin" onClick={() => setIsMenuOpen(false)}>Admin Dashboard</Link>
        </li>
        <list>
        <Link to="/profile" onClick={() => setIsMenuOpen(false)}> Profile</Link>
        </list>
      </ul>
    </nav>
  );
};

export default Navbar;