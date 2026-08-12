/**
 * SmartFit Login Page
 *
 * This page provides the frontend login experience.
 *
 * The page communicates with the SmartFit FastAPI backend
 * through the authentication service.
 *
 * Current responsibilities:
 *
 * 1. Collect the user's email and password.
 * 2. Perform basic client-side validation.
 * 3. Send credentials to the FastAPI login endpoint.
 * 4. Store the returned JWT access token.
 * 5. Display authentication errors.
 * 6. Redirect the authenticated user to the dashboard.
 *
 * IMPORTANT:
 * The frontend does NOT hash the password.
 * Password verification is handled by the backend.
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { loginUser } from "../services/authService";


function Login() {
  // React Router navigation function.
  // Used to redirect the user after successful login.
  const navigate = useNavigate();


  // Store the values entered into the login form.
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });


  // Store validation or authentication errors.
  const [error, setError] = useState("");


  // Store a successful login message.
  const [success, setSuccess] = useState("");


  // Track whether the login request is currently running.
  const [loading, setLoading] = useState(false);


  /**
   * Update the appropriate form field whenever
   * the user changes an input.
   */
  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((previousData) => ({
      ...previousData,
      [name]: value,
    }));

    // Clear previous feedback when the user edits the form.
    setError("");
    setSuccess("");
  }


  /**
   * Validate the login form before contacting the backend.
   *
   * Returns:
   *     An error message if validation fails.
   *     An empty string if the form is valid.
   */
  function validateForm() {
    const email = formData.email.trim();

    // Ensure both fields have been provided.
    if (!email || !formData.password) {
      return "Please enter your email and password.";
    }

    // Perform basic email validation.
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(email)) {
      return "Please enter a valid email address.";
    }

    return "";
  }


  /**
   * Handle login form submission.
   *
   * This function now communicates with the real
   * FastAPI authentication endpoint.
   */
  async function handleSubmit(event) {
    event.preventDefault();

    // Clear previous feedback.
    setError("");
    setSuccess("");


    // Validate the submitted information.
    const validationError = validateForm();

    if (validationError) {
      setError(validationError);
      return;
    }


    // Indicate that authentication is being processed.
    setLoading(true);


    try {
      /**
       * Send the user's credentials to FastAPI.
       *
       * The authentication service handles the actual
       * API request.
       */
      const response = await loginUser({
        email: formData.email.trim(),
        password: formData.password,
      });


      /**
       * Handle unsuccessful authentication responses.
       *
       * FastAPI returns an error status when the credentials
       * are invalid.
       */
      if (!response.ok) {
        let message = "Login failed. Please check your credentials.";

        try {
          const errorData = await response.json();

          // FastAPI commonly returns an error message in
          // the "detail" property.
          if (errorData.detail) {
            message = errorData.detail;
          }
        } catch {
          // Keep the default error message if the response
          // does not contain valid JSON.
        }

        setError(message);
        return;
      }


      /**
       * Read the successful login response.
       *
       * The SmartFit backend returns a JWT access token.
       */
      const data = await response.json();


      if (!data.access_token) {
        setError(
          "Login succeeded, but no authentication token was received."
        );
        return;
      }


      /**
       * Store the JWT locally.
       *
       * We use localStorage for the current development
       * implementation so the authentication state survives
       * page refreshes.
       *
       * We will centralize this authentication state later
       * when we implement AuthContext.
       */
      localStorage.setItem(
        "smartfit_token",
        data.access_token
      );


      // Display a short success message.
      setSuccess("Login successful! Redirecting...");


      /**
       * Redirect the authenticated user to the dashboard.
       *
       * A short delay allows the success message to be visible
       * before navigation.
       */
      setTimeout(() => {
        navigate("/dashboard");
      }, 800);


    } catch (requestError) {
      /**
       * This catches network-level errors such as:
       *
       * - FastAPI server being offline
       * - Incorrect API URL
       * - Network failure
       * - Browser blocking the request
       */
      console.error("Login request failed:", requestError);

      setError(
        "Unable to connect to SmartFit. Please make sure the server is running and try again."
      );


    } finally {
      // Always stop the loading state once the request finishes.
      setLoading(false);
    }
  }


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