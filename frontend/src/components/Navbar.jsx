import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

function Navbar() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setMobileMenuOpen(false);
  };

  // Vérifier si le lien est actif
  const isActive = (path) => {
    return location.pathname === path ? 'active' : '';
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo" onClick={closeMobileMenu}>
          <span className="logo-text">IA-WebAgency</span>
        </Link>

        <div className="menu-icon" onClick={toggleMobileMenu}>
          <i className={mobileMenuOpen ? 'fas fa-times' : 'fas fa-bars'} />
        </div>

        <ul className={mobileMenuOpen ? 'nav-menu active' : 'nav-menu'}>
          <li className="nav-item">
            <Link 
              to="/" 
              className={`nav-link ${isActive('/')}`} 
              onClick={closeMobileMenu}
            >
              Tableau de bord
            </Link>
          </li>
          <li className="nav-item">
            <Link 
              to="/projects/new" 
              className={`nav-link ${isActive('/projects/new')}`} 
              onClick={closeMobileMenu}
            >
              Nouveau Projet
            </Link>
          </li>
          <li className="nav-item">
            <Link 
              to="/knowledge" 
              className={`nav-link ${isActive('/knowledge')}`} 
              onClick={closeMobileMenu}
            >
              Base de Connaissances
            </Link>
          </li>
        </ul>
      </div>
    </nav>
  );
}

export default Navbar;