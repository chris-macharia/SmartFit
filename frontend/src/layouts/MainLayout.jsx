/**
 * SmartFit Main Application Layout
 *
 * Provides the common structure shared by SmartFit pages:
 *
 *     Navbar
 *        ↓
 *     Page Content
 *        ↓
 *     Footer
 *
 * React Router's Outlet renders the page associated
 * with the current URL.
 */

import { Outlet } from "react-router-dom";

import Navbar from "../components/Navbar";
import Footer from "../components/Footer";


function MainLayout() {
  return (
    <div className="app-layout">

      {/* Shared SmartFit navigation. */}
      <Navbar />

      {/* Current route is rendered inside the main content area. */}
      <main className="main-content">
        <Outlet />
      </main>

      {/* Shared SmartFit footer. */}
      <Footer />

    </div>
  );
}


export default MainLayout;