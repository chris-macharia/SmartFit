/**
 * SmartFit Login Page
 *
 * This page provides the frontend login experience.
 *
 * At this stage, authentication is simulated locally.
 * The FastAPI JWT authentication endpoint will be connected
 * later during the backend integration phase.
 *
 * Current responsibilities:
 *
 * 1. Collect the user's email and password.
 * 2. Perform basic client-side validation.
 * 3. Display validation and authentication messages.
 * 4. Simulate a successful login.
 * 5. Redirect the user to the dashboard.
 *
 * IMPORTANT:
 * No credentials are sent to the backend yet.
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";


function Login() {
  // React Router navigation function.
  // Used to redirect the user after successful login.
  const navigate = useNavigate();


  // Store the values entered into the login form.
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });


  // Store validation or login errors.
  const [error, setError] = useState("");


  // Store a successful login message.
  const [success, setSuccess] = useState("");


  // Track whether the login operation is currently running.
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
   * Validate the login form before attempting authentication.
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
   * Backend authentication is intentionally not performed yet.
   *
   * Later, this function will call the authentication service,
   * which will communicate with the FastAPI JWT login endpoint.
   */
  function handleSubmit(event) {
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


    /**
     * Simulate a login request.
     *
     * This gives us a realistic frontend experience while
     * keeping the frontend independent from the backend.
     */
    setTimeout(() => {

      setLoading(false);

      setSuccess(
        "Login successful! Redirecting..."
      );


      // Redirect to the dashboard after the success message.
      setTimeout(() => {
        navigate("/dashboard");
      }, 800);

    }, 800);
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