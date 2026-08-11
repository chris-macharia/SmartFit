/**
 * SmartFit Registration Page
 *
 * This page provides the frontend registration experience.
 *
 * Registration is now connected to the SmartFit FastAPI backend.
 *
 * Current responsibilities:
 *
 * 1. Collect registration information.
 * 2. Perform basic client-side validation.
 * 3. Send valid registration data to FastAPI.
 * 4. Display backend validation or registration errors.
 * 5. Display a success message after account creation.
 * 6. Redirect the user to the login page after successful registration.
 *
 * IMPORTANT:
 * Password hashing is NOT performed in the frontend.
 * The password is sent to the FastAPI backend over the API connection,
 * where the backend hashes it before storing it in PostgreSQL.
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

// Authentication service responsible for communicating with
// the SmartFit registration endpoint.
import { registerUser } from "../services/authService";


function Register() {
  // React Router navigation function.
  // Used to redirect the user to the login page after
  // successful account creation.
  const navigate = useNavigate();


  // Store all values entered into the registration form.
  //
  // confirm_password is intentionally kept only on the frontend.
  // It is used to verify that the user entered the same password
  // twice, but it is NOT sent to the backend.
  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    password: "",
    confirm_password: "",
    role: "customer",
  });


  // Store validation or backend registration errors.
  const [error, setError] = useState("");


  // Store a successful registration message.
  const [success, setSuccess] = useState("");


  // Track whether the registration request is currently being sent.
  //
  // This prevents the user from submitting the form multiple times
  // while the backend is processing the request.
  const [loading, setLoading] = useState(false);


  /**
   * Update the appropriate form field when the user types.
   *
   * The input's "name" attribute determines which value is updated.
   */
  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((previousData) => ({
      ...previousData,
      [name]: value,
    }));

    // Clear previous messages when the user modifies the form.
    setError("");
    setSuccess("");
  }


  /**
   * Validate the registration form before contacting the backend.
   *
   * Returns:
   *   A validation error message, or an empty string if valid.
   */
  function validateForm() {
    // Remove unnecessary whitespace from the name and email.
    const fullName = formData.full_name.trim();
    const email = formData.email.trim();


    // Check that all required fields have been provided.
    if (!fullName || !email || !formData.password) {
      return "Please complete all required fields.";
    }


    // Check that the password is long enough.
    //
    // This provides immediate feedback instead of sending
    // obviously invalid data to the backend.
    if (formData.password.length < 8) {
      return "Password must contain at least 8 characters.";
    }


    // Confirm that both password fields match.
    if (formData.password !== formData.confirm_password) {
      return "Passwords do not match.";
    }


    // Perform basic email format validation.
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(email)) {
      return "Please enter a valid email address.";
    }


    // No client-side validation errors were found.
    return "";
  }


  /**
   * Convert FastAPI error responses into a user-friendly message.
   *
   * FastAPI can return validation errors in several formats.
   * This helper keeps that backend-specific handling out of
   * the main form submission function.
   */
  async function getErrorMessage(response) {
    try {
      const data = await response.json();

      // FastAPI commonly returns:
      //
      // {
      //   "detail": "..."
      // }
      //
      // for application-level errors.
      if (typeof data.detail === "string") {
        return data.detail;
      }


      // FastAPI validation errors can return an array under
      // the "detail" property. Extract the first useful message.
      if (Array.isArray(data.detail) && data.detail.length > 0) {
        const firstError = data.detail[0];

        if (firstError?.msg) {
          return firstError.msg;
        }
      }


      // Fallback when the backend returns an unexpected format.
      return "Registration failed. Please check your information and try again.";
    } catch {
      // If the response cannot be interpreted as JSON,
      // provide a generic message rather than exposing
      // an internal browser or server error.
      return "Unable to complete registration. Please try again.";
    }
  }


  /**
   * Handle registration form submission.
   *
   * This now performs the complete frontend-to-backend
   * registration flow.
   */
  async function handleSubmit(event) {
    // Prevent the browser from performing a traditional
    // page reload when the form is submitted.
    event.preventDefault();


    // Clear previous messages.
    setError("");
    setSuccess("");


    // Prevent duplicate submissions if the user somehow
    // submits while another request is already running.
    if (loading) {
      return;
    }


    // Validate the submitted information before contacting
    // the backend.
    const validationError = validateForm();

    if (validationError) {
      setError(validationError);
      return;
    }


    // Indicate that the registration request is being processed.
    setLoading(true);


    try {
      /**
       * Only send the fields expected by the backend.
       *
       * confirm_password is intentionally excluded because
       * it exists only for frontend validation.
       */
      const registrationData = {
        full_name: formData.full_name.trim(),
        email: formData.email.trim(),
        password: formData.password,
        role: formData.role,
      };


      // Send the registration request through our authentication
      // service instead of making a fetch request directly here.
      const response = await registerUser(registrationData);


      // FastAPI returns a successful HTTP status when the user
      // has been created successfully.
      if (!response.ok) {
        // Convert the backend error into a user-friendly message.
        const message = await getErrorMessage(response);
        setError(message);
        return;
      }


      // Registration was successful.
      setSuccess(
        "Account created successfully! Redirecting to login..."
      );


      /**
       * Give the user a moment to see the success message before
       * redirecting them to the login page.
       */
      setTimeout(() => {
        navigate("/login");
      }, 1200);

    } catch (requestError) {
      /**
       * This normally means the browser could not reach the
       * backend at all.
       *
       * Examples:
       * - FastAPI is not running.
       * - Incorrect API URL.
       * - Network connection problem.
       * - CORS configuration problem.
       */
      console.error("Registration request failed:", requestError);

      setError(
        "Unable to connect to SmartFit. Please make sure the server is running and try again."
      );

    } finally {
      // Always stop the loading state after the request finishes,
      // whether it succeeded or failed.
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
            SMARTFIT ACCOUNT
          </p>

          <h1>
            Create your account
          </h1>

          <p>
            Start your personalized virtual fitting experience.
          </p>

        </div>


        {/* =================================================
            REGISTRATION FORM
            ================================================= */}

        <form
          className="auth-form"
          onSubmit={handleSubmit}
          noValidate
        >

          {/* Full name */}
          <div className="form-group">

            <label htmlFor="full_name">
              Full Name
            </label>

            <input
              id="full_name"
              name="full_name"
              type="text"
              value={formData.full_name}
              onChange={handleChange}
              placeholder="Enter your full name"
              autoComplete="name"
            />

          </div>


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
              placeholder="Create a password"
              autoComplete="new-password"
            />

            <small className="form-help">
              Use at least 8 characters.
            </small>

          </div>


          {/* Confirm password */}
          <div className="form-group">

            <label htmlFor="confirm_password">
              Confirm Password
            </label>

            <input
              id="confirm_password"
              name="confirm_password"
              type="password"
              value={formData.confirm_password}
              onChange={handleChange}
              placeholder="Confirm your password"
              autoComplete="new-password"
            />

          </div>


          {/* Account type */}
          <div className="form-group">

            <label htmlFor="role">
              Account Type
            </label>

            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
            >

              <option value="customer">
                Customer
              </option>

              <option value="retailer">
                Retailer
              </option>

            </select>

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
              ? "Creating Account..."
              : "Create Account"}
          </button>

        </form>


        {/* =================================================
            LOGIN LINK
            ================================================= */}

        <p className="auth-footer">

          Already have an account?{" "}

          <Link to="/login">
            Log in
          </Link>

        </p>

      </section>

    </main>
  );
}


export default Register;

