/**
 * SmartFit Registration Page
 *
 * This page provides the frontend registration experience.
 *
 * At this stage of development, registration is handled locally.
 * The FastAPI registration endpoint will be connected later during
 * the backend integration phase.
 *
 * Current responsibilities:
 *
 * 1. Collect registration information.
 * 2. Validate the information on the client.
 * 3. Display validation and success messages.
 * 4. Simulate successful account creation.
 * 5. Redirect the user to the login page.
 *
 * IMPORTANT:
 * Password hashing is NOT performed in the frontend.
 * When backend integration is implemented, the password will be
 * sent securely to FastAPI, where it will be hashed before storage.
 */

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";


function Register() {
  // React Router navigation function.
  // This allows us to redirect the user after registration.
  const navigate = useNavigate();


  // Store all values entered into the registration form.
  const [formData, setFormData] = useState({
    full_name: "",
    email: "",
    password: "",
    confirm_password: "",
    role: "customer",
  });


  // Store validation or registration errors.
  const [error, setError] = useState("");


  // Store a successful registration message.
  const [success, setSuccess] = useState("");


  // Track whether the form is currently being submitted.
  const [loading, setLoading] = useState(false);


  /**
   * Update the appropriate form field when the user types.
   *
   * Rather than creating a separate function for every input,
   * the input's "name" attribute determines which value is updated.
   */
  function handleChange(event) {
    const { name, value } = event.target;

    setFormData((previousData) => ({
      ...previousData,
      [name]: value,
    }));

    // Clear previous messages when the user edits the form.
    setError("");
    setSuccess("");
  }


  /**
   * Validate the registration form.
   *
   * This performs basic frontend validation before the form
   * would eventually be submitted to the backend.
   *
   * Returns:
   *     A validation error message, or an empty string if valid.
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
    if (formData.password.length < 8) {
      return "Password must contain at least 8 characters.";
    }


    // Check that both password fields match.
    if (formData.password !== formData.confirm_password) {
      return "Passwords do not match.";
    }


    // Basic email format validation.
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(email)) {
      return "Please enter a valid email address.";
    }


    // No validation errors were found.
    return "";
  }


  /**
   * Handle registration form submission.
   *
   * The backend is intentionally NOT called yet.
   *
   * We simulate a successful registration so that we can
   * finish and test the frontend independently.
   */
  function handleSubmit(event) {
    event.preventDefault();

    // Clear previous messages.
    setError("");
    setSuccess("");


    // Validate the submitted information.
    const validationError = validateForm();

    if (validationError) {
      setError(validationError);
      return;
    }


    // Indicate that registration is being processed.
    setLoading(true);


    /**
     * Simulate a short registration request.
     *
     * Later this block will be replaced with a call to an API
     * service such as:
     *
     * registerUser(formData)
     */
    setTimeout(() => {

      setLoading(false);

      setSuccess(
        "Account created successfully! Redirecting to login..."
      );


      // Redirect the user to the login page after the
      // success message has been displayed briefly.
      setTimeout(() => {
        navigate("/login");
      }, 1200);

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