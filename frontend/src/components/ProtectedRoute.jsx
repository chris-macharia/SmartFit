/**
 * SmartFit Protected Route
 *
 * Prevents unauthenticated users from accessing
 * pages that require a valid SmartFit account.
 *
 * The route waits for AuthContext to finish checking
 * the stored JWT before deciding whether the user
 * should be allowed to continue.
 */

import { Navigate, Outlet, useLocation } from "react-router-dom";

import { useAuth } from "../context/AuthContext";


function ProtectedRoute() {
  /*
   * Get the current authentication state from
   * the centralized AuthContext.
   */
  const {
    isAuthenticated,
    loading,
  } = useAuth();


  /*
   * Remember the page the user originally attempted
   * to access.
   *
   * This will be useful later when we improve the
   * login experience.
   */
  const location = useLocation();


  /*
   * Authentication is still being checked.
   *
   * We must wait before redirecting because the JWT
   * may still be being validated by the backend.
   */
  if (loading) {
    return (
      <main className="auth-page">
        <section className="auth-card">
          <div className="auth-heading">
            <p className="section-label">
              SMARTFIT
            </p>

            <h1>
              Checking your session...
            </h1>

            <p>
              Please wait while we verify your account.
            </p>
          </div>
        </section>
      </main>
    );
  }


  /*
   * If there is no authenticated user, redirect
   * to the login page.
   *
   * Replace the current browser history entry so
   * the user doesn't return to the protected page
   * simply by pressing the Back button.
   */
  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
        state={{
          from: location,
        }}
      />
    );
  }


  /*
   * The user is authenticated.
   *
   * Outlet renders whichever protected route
   * is currently being requested.
   */
  return <Outlet />;
}


export default ProtectedRoute;