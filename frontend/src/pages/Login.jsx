/**
 * SmartFit Login Page
 *
 * This page provides the frontend login experience.
 *
 * Authentication is handled through AuthContext.
 *
 * Current responsibilities:
 *
 * 1. Collect the user's email and password.
 * 2. Perform basic client-side validation.
 * 3. Call the centralized authentication system.
 * 4. Display validation and authentication messages.
 * 5. Redirect successfully authenticated users
 *    to the dashboard.
 *
 * The actual communication with FastAPI is handled by
 * AuthContext and the authentication service.
 */


import { useState } from "react";

import {
  Link,
  useNavigate,
} from "react-router-dom";

import { useAuth } from "../context/AuthContext";


function Login() {

  /*
   * React Router navigation function.
   *
   * Used to redirect the user after successful login.
   */
  const navigate = useNavigate();


  /*
   * Retrieve the centralized login function
   * from AuthContext.
   */
  const { login } = useAuth();


  /*
   * Store the values entered into the login form.
   */
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });


  /*
   * Store validation or login errors.
   */
  const [error, setError] = useState("");


  /*
   * Store a successful login message.
   */
  const [success, setSuccess] = useState("");


  /*
   * Track whether the login operation is currently running.
   */
  const [loading, setLoading] = useState(false);


  // ==========================================================
  // HANDLE INPUT CHANGES
  // ==========================================================

  /**
   * Update the appropriate form field whenever
   * the user changes an input.
   */
  function handleChange(event) {

    const {
      name,
      value,
    } = event.target;


    /*
     * Update only the field that changed.
     */
    setFormData((previousData) => ({
      ...previousData,
      [name]: value,
    }));


    /*
     * Clear previous feedback when the user
     * edits the form.
     */
    setError("");
    setSuccess("");
  }


  // ==========================================================
  // FORM VALIDATION
  // ==========================================================

  /**
   * Validate the login form before authentication.
   *
   * Returns:
   *
   * - An error message if validation fails.
   * - An empty string if the form is valid.
   */
  function validateForm() {

    /*
     * Remove unnecessary whitespace from the email.
     */
    const email = formData.email.trim();


    /*
     * Make sure both fields have been provided.
     */
    if (!email || !formData.password) {

      return "Please enter your email and password.";
    }


    /*
     * Perform basic email validation.
     */
    const emailPattern =
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


    if (!emailPattern.test(email)) {

      return "Please enter a valid email address.";
    }


    /*
     * No validation errors were found.
     */
    return "";
  }


  // ==========================================================
  // FORM SUBMISSION
  // ==========================================================

  /**
   * Handle login form submission.
   *
   * Authentication is delegated to AuthContext.
   */
  async function handleSubmit(event) {

    /*
     * Prevent the browser from performing a normal
     * HTML form submission.
     */
    event.preventDefault();


    /*
     * Clear previous feedback.
     */
    setError("");
    setSuccess("");


    /*
     * Validate the submitted information.
     */
    const validationError = validateForm();


    if (validationError) {

      setError(validationError);

      return;
    }


    /*
     * Indicate that authentication is being processed.
     */
    setLoading(true);


    try {

      /*
       * Authenticate the user through AuthContext.
       *
       * AuthContext handles:
       *
       * - FastAPI login
       * - JWT storage
       * - Current-user retrieval
       * - Updating the global user state
       */
      await login({

        /*
         * Trim the email before sending it
         * to the backend.
         */
        email: formData.email.trim(),

        /*
         * Password is sent exactly as entered.
         */
        password: formData.password,
      });


      /*
       * At this point AuthContext has already updated
       * isAuthenticated to true.
       */
      setSuccess(
        "Login successful! Redirecting..."
      );


      /*
       * Give the user a short moment to see the
       * success message before changing pages.
       */
      setTimeout(() => {

        navigate("/dashboard");

      }, 800);

    } catch (requestError) {

      /*
       * Log the technical error for development.
       */
      console.error(
        "Login request failed:",
        requestError
      );


      /*
       * Display a user-friendly error message.
       */
      setError(
        requestError.message ||
        "Unable to connect to SmartFit. Please make sure the server is running and try again."
      );

    } finally {

      /*
       * Authentication has finished.
       */
      setLoading(false);
    }
  }


  // ==========================================================
  // PAGE
  // ==========================================================

  return (
    <main className="auth-page">


      <section className="auth-card">


        {/* =================================================
            PAGE HEADER
            ================================================= */}

        <div className="auth-heading">


          <p className="section-label">
            WELCOME BACK
          </p>


          <h1>
            Log in to SmartFit
          </h1>


          <p>
            Continue your personalized virtual fitting experience.
          </p>


        </div>


        {/* =================================================
            LOGIN FORM
            ================================================= */}

        <form
          className="auth-form"
          onSubmit={handleSubmit}
          noValidate
        >


          {/* Email address */}

          <div className="form-group">


            <label htmlFor="email">
              Email Address
            </label>


            <input
              id="email"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              autoComplete="email"
            />


          </div>


          {/* Password */}

          <div className="form-group">


            <label htmlFor="password">
              Password
            </label>


            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              autoComplete="current-password"
            />


          </div>


          {/* =================================================
              FEEDBACK MESSAGES
              ================================================= */}

          {error && (

            <div
              className="form-message error-message"
              role="alert"
            >
              {error}
            </div>

          )}


          {success && (

            <div
              className="form-message success-message"
              role="status"
            >
              {success}
            </div>

          )}


          {/* =================================================
              SUBMIT BUTTON
              ================================================= */}

          <button
            type="submit"
            className="primary-button auth-submit"
            disabled={loading}
          >

            {loading
              ? "Signing In..."
              : "Log In"}

          </button>


        </form>


        {/* =================================================
            REGISTRATION LINK
            ================================================= */}

        <p className="auth-footer">


          Don't have an account?{" "}


          <Link to="/register">
            Create an account
          </Link>


        </p>


      </section>


    </main>
  );
}


export default Login;