/**
 * SmartFit Authentication Context
 *
 * This module provides centralized authentication state
 * for the entire SmartFit React application.
 *
 * Responsibilities:
 *
 * 1. Store the currently authenticated user.
 * 2. Restore an existing authentication session when
 *    the application starts.
 * 3. Authenticate users through the FastAPI backend.
 * 4. Store the JWT returned by the backend.
 * 5. Retrieve the currently authenticated user.
 * 6. Provide logout functionality.
 * 7. Expose authentication state to React components.
 */

import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  loginUser,
  getCurrentUser,
} from "../services/authService";


// ============================================================
// AUTHENTICATION CONTEXT
// ============================================================

/*
 * Create the authentication context.
 *
 * The context allows authentication information to be
 * shared throughout the application without passing it
 * manually through every component.
 */
const AuthContext = createContext(null);


// ============================================================
// AUTHENTICATION PROVIDER
// ============================================================

/**
 * AuthProvider
 *
 * This component wraps the SmartFit application and
 * provides authentication information to all child
 * components.
 */
export function AuthProvider({ children }) {

  /*
   * Store the currently authenticated user.
   *
   * null means that no authenticated user is currently
   * available.
   */
  const [user, setUser] = useState(null);


  /*
   * Track whether the application is still checking
   * the user's existing authentication session.
   *
   * This prevents protected routes from redirecting
   * before we have finished checking localStorage.
   */
  const [loading, setLoading] = useState(true);


  // ==========================================================
  // RESTORE EXISTING AUTHENTICATION
  // ==========================================================

  /**
   * Restore authentication when the application starts.
   *
   * If a JWT was previously stored in localStorage,
   * we send it to the backend's current-user endpoint.
   *
   * This allows SmartFit to remember that the user is
   * authenticated even after refreshing the browser.
   */
  useEffect(() => {

    async function restoreAuthentication() {

      /*
       * Retrieve the JWT saved during login.
       */
      const token = localStorage.getItem(
        "smartfit_token"
      );


      /*
       * If there is no token, there is no existing
       * authentication session to restore.
       */
      if (!token) {

        setLoading(false);

        return;
      }


      try {

        /*
         * Ask FastAPI to validate the JWT and return
         * the user associated with that token.
         */
        const response = await getCurrentUser(token);


        /*
         * A failed response normally means that the
         * token has expired or is no longer valid.
         */
        if (!response.ok) {

          /*
           * Remove the invalid token so that it cannot
           * continue to be used by the application.
           */
          localStorage.removeItem(
            "smartfit_token"
          );


          /*
           * Make sure there is no authenticated user.
           */
          setUser(null);

          return;
        }


        /*
         * Convert the backend response into a
         * JavaScript object.
         */
        const currentUser = await response.json();


        /*
         * Store the authenticated user in React state.
         *
         * This makes the user available throughout
         * the SmartFit application.
         */
        setUser(currentUser);

      } catch (error) {

        /*
         * A network error can occur if the FastAPI
         * server is unavailable.
         */
        console.error(
          "Unable to restore authentication:",
          error
        );


        /*
         * Remove the token because we cannot establish
         * a valid authenticated session.
         */
        localStorage.removeItem(
          "smartfit_token"
        );


        setUser(null);

      } finally {

        /*
         * Authentication checking has now finished,
         * regardless of whether it succeeded or failed.
         */
        setLoading(false);
      }
    }


    /*
     * Start the authentication restoration process.
     */
    restoreAuthentication();

  }, []);


  // ==========================================================
  // LOGIN
  // ==========================================================

  /**
   * Authenticate a SmartFit user.
   *
   * This function is now the central login function
   * for the entire frontend.
   *
   * The Login page does not communicate directly with
   * the backend anymore. Instead, it calls this function.
   *
   * Flow:
   *
   * 1. Send credentials to FastAPI.
   * 2. Receive JWT.
   * 3. Store JWT in localStorage.
   * 4. Request the current user.
   * 5. Store the authenticated user in React state.
   */
  async function login(credentials) {

    /*
     * Send the user's email and password to the
     * FastAPI login endpoint.
     */
    const response = await loginUser(credentials);


    /*
     * Handle an unsuccessful login request.
     */
    if (!response.ok) {

      /*
       * Default error message.
       */
      let message =
        "Login failed. Please check your credentials.";


      try {

        /*
         * FastAPI normally returns an error response
         * containing a "detail" field.
         */
        const errorData = await response.json();


        if (errorData.detail) {

          message = errorData.detail;
        }

      } catch {

        /*
         * If the backend response cannot be parsed,
         * keep the default error message.
         */
      }


      /*
       * Throw an error so that Login.jsx can display
       * the message to the user.
       */
      throw new Error(message);
    }


    // ========================================================
    // PROCESS SUCCESSFUL LOGIN
    // ========================================================

    /*
     * Convert the successful response into an object.
     */
    const data = await response.json();


    /*
     * Make sure the backend actually returned
     * an authentication token.
     */
    if (!data.access_token) {

      throw new Error(
        "Login succeeded, but no authentication token was received."
      );
    }


    /*
     * Store the JWT locally.
     *
     * The token will later be used to authenticate
     * requests to protected SmartFit API endpoints.
     */
    localStorage.setItem(
      "smartfit_token",
      data.access_token
    );


    // ========================================================
    // RETRIEVE CURRENT USER
    // ========================================================

    /*
     * Immediately retrieve the authenticated user.
     *
     * This is important because it updates AuthContext
     * immediately after login.
     *
     * We do NOT have to wait for the application to
     * restart or refresh.
     */
    const userResponse = await getCurrentUser(
      data.access_token
    );


    /*
     * If the token was accepted by the login endpoint
     * but the current-user endpoint fails, we should
     * not leave an unusable token in localStorage.
     */
    if (!userResponse.ok) {

      localStorage.removeItem(
        "smartfit_token"
      );


      throw new Error(
        "Login succeeded, but the user session could not be established."
      );
    }


    /*
     * Convert the current-user response into
     * a JavaScript object.
     */
    const authenticatedUser =
      await userResponse.json();


    /*
     * Store the authenticated user globally.
     *
     * ProtectedRoute can now immediately see that
     * the user is authenticated.
     */
    setUser(authenticatedUser);


    /*
     * Return the authenticated user to the component
     * that called the login function.
     */
    return authenticatedUser;
  }


  // ==========================================================
  // LOGOUT
  // ==========================================================

  /**
   * Log the current user out of SmartFit.
   *
   * JWT authentication is stateless on the backend,
   * so logging out on the frontend primarily means
   * removing the stored token and clearing the user
   * from React state.
   */
  function logout() {

    /*
     * Remove the JWT from localStorage.
     */
    localStorage.removeItem(
      "smartfit_token"
    );


    /*
     * Clear the authenticated user.
     */
    setUser(null);
  }


  // ==========================================================
  // AUTHENTICATION STATE
  // ==========================================================

  /*
   * These values are made available to every component
   * inside AuthProvider.
   */
  const value = {

    /*
     * The currently authenticated user.
     */
    user,

    /*
     * Indicates whether authentication restoration
     * is still in progress.
     */
    loading,

    /*
     * Convenient boolean indicating whether a user
     * is currently authenticated.
     */
    isAuthenticated: Boolean(user),

    /*
     * Centralized login function.
     */
    login,

    /*
     * Centralized logout function.
     */
    logout,
  };


  // ==========================================================
  // PROVIDER
  // ==========================================================

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}


// ============================================================
// USE AUTH HOOK
// ============================================================

/**
 * useAuth
 *
 * Custom React hook used by components that need
 * authentication information.
 *
 * Example:
 *
 * const {
 *   user,
 *   isAuthenticated,
 *   logout,
 * } = useAuth();
 */
export function useAuth() {

  /*
   * Retrieve the authentication context.
   */
  const context = useContext(AuthContext);


  /*
   * Prevent the hook from being used outside
   * of AuthProvider.
   */
  if (!context) {

    throw new Error(
      "useAuth must be used inside an AuthProvider."
    );
  }


  /*
   * Return the authentication state and functions.
   */
  return context;
}