/**
 * SmartFit Footer
 *
 * Provides the shared footer displayed across the application.
 *
 * The footer contains the application name, a short description,
 * and the current development year.
 */

function Footer() {
  return (
    <footer className="footer">

      {/* SmartFit branding and description. */}
      <div className="footer-content">

        <div>
          <h3>👕 SmartFit</h3>

          <p>
            Virtual fitting technology for smarter online
            clothing shopping.
          </p>
        </div>

        {/* Development information. */}
        <div className="footer-info">
          <p>
            SmartFit — Virtual Fitting System
          </p>

          <p>
            © 2026 SmartFit
          </p>
        </div>

      </div>

    </footer>
  );
}

export default Footer;