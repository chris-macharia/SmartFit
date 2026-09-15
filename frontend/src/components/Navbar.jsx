/**
 * SmartFit Navigation Bar
 *
 * Provides:
 *
 * - SmartFit branding.
 * - Navigation links.
 * - Current authenticated user information.
 * - Logout functionality.
 * - Light/dark mode toggle.
 *
 * Authentication information is obtained from AuthContext.
 * This keeps the Navbar independent from the authentication
 * implementation and allows it to react automatically when
 * the user's authentication state changes.
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";


function Navbar() {
  const {
    user,
    isAuthenticated,
    logout,
  } = useAuth();

  const navigate = useNavigate();

  const [darkMode, setDarkMode] = useState(false);


  /**
   * Toggle between light and dark mode.
   *
   * The existing theme behaviour is preserved.
   */
  const toggleDarkMode = () => {
    setDarkMode((currentMode) => {
      const newMode = !currentMode;

      document.body.classList.toggle(
        "dark-mode",
        newMode
      );

      return newMode;
    });
  };


  /**
   * Log the user out and return them to the login page.
   *
   * The existing authentication flow is preserved.
   */
  function handleLogout() {
    logout();
    navigate("/login");
  }


  return (
    <nav className="navbar">

      {/* ---------------------------------------------------
          SmartFit branding
          --------------------------------------------------- */}

      <Link
        to="/"
        className="navbar-brand"
        aria-label="SmartFit home"
      >
        <img
          src="/smartfit-logo.svg"
          alt=""
          className="navbar-logo"
        />

        <span className="navbar-brand-text">
          SmartFit
        </span>
      </Link>


      {/* ---------------------------------------------------
          Main navigation links
          --------------------------------------------------- */}

      <div className="navbar-links">

        <Link to="/">
          Home
        </Link>


        {isAuthenticated && (
          <Link to="/dashboard">
            Dashboard
          </Link>
        )}


        {isAuthenticated && (
          <Link to="/upload-video">
            Upload Video
          </Link>
        )}


        {!isAuthenticated && (
          <>
            <Link to="/login">
              Login
            </Link>

            <Link to="/register">
              Register
            </Link>
          </>
        )}

      </div>


      {/* ---------------------------------------------------
          Authenticated user controls
          --------------------------------------------------- */}

      {isAuthenticated && user && (
        <div className="navbar-user">

        <div className="navbar-user-info">
          <svg
            className="navbar-user-icon"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              cx="12"
              cy="8"
              r="4"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            />

            <path
              d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>

          <span className="navbar-user-name">
            {user.full_name}
          </span>
        </div>


          <button
            type="button"
            className="navbar-logout"
            onClick={handleLogout}
          >
            Logout
          </button>

        </div>
      )}


      {/* ---------------------------------------------------
          Theme toggle
          --------------------------------------------------- */}

      <div className="theme-control">

        <button
          type="button"
          className={`theme-switch ${
            darkMode ? "active" : ""
          }`}
          onClick={toggleDarkMode}
          aria-label={
            darkMode
              ? "Switch to light mode"
              : "Switch to dark mode"
          }
          aria-pressed={darkMode}
        >

          <span className="theme-switch-handle">
            {darkMode ? "☀️" : "🌙"}
          </span>

        </button>

      </div>

    </nav>
  );
}


export default Navbar;
