/**
 * SmartFit Navigation Bar
 *
 * This component provides the main navigation links used
 * throughout the SmartFit application.
 *
 * React Router's Link component is used instead of normal
 * HTML <a> elements so that navigation happens without
 * reloading the entire React application.
 */

import { Link } from "react-router-dom";


function Navbar() {
  return (
    <nav>
      {/* 
        SmartFit application name/logo.
        
        Clicking the SmartFit logo takes the user back
        to the application's home page.
      */}
      <Link to="/">
        👕 SmartFit
      </Link>


      {/*
        Main navigation links.

        These routes correspond to the pages currently
        available in the SmartFit frontend.
      */}
      <div>
        <Link to="/">Home</Link>
        <Link to="/login">Login</Link>
        <Link to="/register">Register</Link>
      </div>
    </nav>
  );
}


export default Navbar;