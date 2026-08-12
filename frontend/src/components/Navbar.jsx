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
  /*
   * ---------------------------------------------------------
   * AUTHENTICATION
   * ---------------------------------------------------------
   *
   * Get the current authenticated user and logout function
   * from the centralized authentication context.
   *
   * "user" contains information returned by:
   *
   * GET /api/users/me
   *
   * For example:
   *
   * {
   *   full_name: "John Doe",
   *   email: "john@example.com",
   *   role: "customer"
   * }
   */
  const {
    user,
    isAuthenticated,
    logout,
  } = useAuth();


  /*
   * React Router navigation function.
   *
   * Used to redirect the user to the login page after
   * logging out.
   */
  const navigate = useNavigate();


  /*
   * ---------------------------------------------------------
   * DARK MODE
   * ---------------------------------------------------------
   *
   * Store whether dark mode is currently enabled.
   *
   * false = light mode
   * true  = dark mode
   */
  const [darkMode, setDarkMode] = useState(false);


  /*
   * ---------------------------------------------------------
   * TOGGLE DARK MODE
   * ---------------------------------------------------------
   *
   * Apply or remove the dark-mode class from the document
   * body.
   */
  const toggleDarkMode = () => {
    setDarkMode((currentMode) => {
      const newMode = !currentMode;


      /*
       * Add or remove the dark-mode class from <body>.
       */
      document.body.classList.toggle(
        "dark-mode",
        newMode
      );


      return newMode;
    });
  };


  /*
   * ---------------------------------------------------------
   * LOGOUT
   * ---------------------------------------------------------
   *
   * AuthContext is responsible for removing the JWT and
   * clearing the authenticated user.
   *
   * After logout is complete, redirect the user to login.
   */
  function handleLogout() {
    logout();

    navigate("/login");
  }


  return (
    <nav className="navbar">


      {/* =================================================
          SMARTFIT BRANDING
          ================================================= */}

      <Link
        to="/"
        className="navbar-brand"
      >
        👕 SmartFit
      </Link>


      {/* =================================================
          MAIN NAVIGATION
          ================================================= */}

      <div className="navbar-links">


        <Link to="/">
          Home
        </Link>


        {/* Dashboard is only useful to authenticated users. */}
        {isAuthenticated && (
          <Link to="/dashboard">
            Dashboard
          </Link>
        )}


        {/* Upload Video is also an authenticated feature. */}
        {isAuthenticated && (
          <Link to="/upload-video">
            Upload Video
          </Link>
        )}


        {/* Show Login/Register when the user is logged out. */}
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


      {/* =================================================
          AUTHENTICATED USER INFORMATION
          ================================================= */}

      {isAuthenticated && user && (
        <div className="navbar-user">


          {/* Display the user's name. */}
          <div className="navbar-user-info">


            <span className="navbar-user-name">
              {user.full_name}
            </span>

          </div>


          {/* Logout button. */}
          <button
            type="button"
            className="navbar-logout"
            onClick={handleLogout}
          >
            Logout
          </button>


        </div>
      )}


      {/* =================================================
          LIGHT / DARK MODE
          ================================================= */}

      <div className="theme-control">


        <span className="theme-label">
          {darkMode ? "Dark Mode" : "Light Mode"}
        </span>


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
            {darkMode ? "🌙" : "☀️"}
          </span>


        </button>


      </div>


    </nav>
  );
}


export default Navbar;