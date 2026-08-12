/**
 * SmartFit Authentication Context
 *
 * Provides centralized authentication state for the frontend.
 *
 * Responsibilities:
 *
 * 1. Store the currently authenticated user.
 * 2. Restore authentication when the application starts.
 * 3. Validate the stored JWT using /api/users/me.
 * 4. Provide login/logout state to the rest of the application.
 */

import { createContext, useContext, useEffect, useState } from "react";

import { getCurrentUser } from "../services/authService";


// Create the authentication context.
const AuthContext = createContext(null);


/**
 * Authentication provider.
 *
 * This component wraps the SmartFit application and makes
 * authentication information available to child components.
 */
export function AuthProvider({ children }) {

  // Currently authenticated user.
  const [user, setUser] = useState(null);

  // Indicates whether authentication is still being checked.
  const [loading, setLoading] = useState(true);


  /**
   * Restore the user's authentication state when the
   * application starts.
   */
  useEffect(() => {

    async function restoreAuthentication() {

      // Retrieve the JWT saved during login.
      const token = localStorage.getItem("smartfit_token");


      // No token means there is no authenticated session.
      if (!token) {
        setLoading(false);
        return;
      }


      try {

        /**
         * Ask the backend who owns this token.
         *
         * This also verifies that the token is still valid.
         */
        const response = await getCurrentUser(token);


        if (!response.ok) {

          // The token is invalid or expired.
          localStorage.removeItem("smartfit_token");
          setUser(null);

          return;
        }


        // Convert the backend response into a JavaScript object.
        const currentUser = await response.json();


        // Store the authenticated user globally.
        setUser(currentUser);

      } catch (error) {

        console.error(
          "Unable to restore authentication:",
          error
        );

        // If the backend cannot be reached, don't keep
        // an unusable authentication session.
        localStorage.removeItem("smartfit_token");
        setUser(null);

      } finally {

        // Authentication checking has finished.
        setLoading(false);
      }
    }


    restoreAuthentication();

  }, []);


  /**
   * Log the current user out.
   */
  function logout() {

    // Remove the stored JWT.
    localStorage.removeItem("smartfit_token");

    // Remove the authenticated user from application state.
    setUser(null);
  }


  /**
   * Value exposed to all components using AuthContext.
   */
  const value = {
    user,
    loading,
    isAuthenticated: Boolean(user),
    logout,
  };


  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}


/**
 * Custom hook for accessing authentication state.
 *
 * Components can use:
 *
 * const { user, logout } = useAuth();
 */
export function useAuth() {

  const context = useContext(AuthContext);


  if (!context) {
    throw new Error(
      "useAuth must be used inside an AuthProvider."
    );
  }


  return context;
}