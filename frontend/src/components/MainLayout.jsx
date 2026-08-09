/**
 * Main Application Layout
 *
 * This component defines the common structure shared
 * by the main SmartFit pages.
 *
 * The layout consists of:
 *
 *     Navbar
 *        ↓
 *     Page Content
 *        ↓
 *     Footer
 *
 * React Router's <Outlet /> is used as a placeholder
 * for the page that matches the current URL.
 */

import { Outlet } from "react-router-dom";

import Navbar from "../components/Navbar";
import Footer from "../components/Footer";


function MainLayout() {
  return (
    <div>

      {/* 
        Shared navigation displayed at the top
        of the application.
      */}
      <Navbar />


      {/*
        Main application content.

        React Router replaces <Outlet /> with the
        component associated with the current route.

        For example:

            /          → Home
            /login     → Login
            /register  → Register
            /dashboard → Dashboard
      */}
      <main>
        <Outlet />
      </main>


      {/*
        Shared footer displayed below the page content.
      */}
      <Footer />

    </div>
  );
}


export default MainLayout;