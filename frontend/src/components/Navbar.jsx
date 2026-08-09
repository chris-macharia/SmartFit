/**
 * SmartFit Navigation Bar
 *
 * Provides:
 *
 * - SmartFit branding.
 * - Navigation links.
 * - Light/dark mode toggle.
 *
 * Dark mode is intentionally kept simple.
 * The selected mode is applied to the entire document body.
 */

import { useState } from "react";
import { Link } from "react-router-dom";


function Navbar() {

  /*
   * Store whether dark mode is currently enabled.
   *
   * false = light mode
   * true  = dark mode
   */
  const [darkMode, setDarkMode] = useState(false);


  /*
   * Toggle the application's colour theme.
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


  return (
    <nav className="navbar">

      {/* SmartFit application branding. */}
      <Link
        to="/"
        className="navbar-brand"
      >
        👕 SmartFit
      </Link>


      {/* Main navigation links. */}
      <div className="navbar-links">

        <Link to="/">
          Home
        </Link>

        <Link to="/login">
          Login
        </Link>

        <Link to="/register">
          Register
        </Link>

        <Link to="/dashboard">
          Dashboard
        </Link>

      </div>


      {/* Light/dark mode toggle switch. */}
      <div className="theme-control">

        <span className="theme-label">
          {darkMode ? "Dark Mode" : "Light Mode"}
        </span>

        <button
          type="button"
          className={`theme-switch ${darkMode ? "active" : ""}`}
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