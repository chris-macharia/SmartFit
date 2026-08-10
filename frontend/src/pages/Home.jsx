/**
 * SmartFit Home Page
 *
 * This is the public landing page for SmartFit.
 *
 * The page introduces:
 *
 * - What SmartFit does.
 * - How the virtual fitting process works.
 * - The main benefits of the system.
 * - A call-to-action for new users.
 *
 * This page is currently presentation-only.
 * Backend functionality will be connected in later stages.
 */

import { Link } from "react-router-dom";


function Home() {
  return (
    <div className="home-page">

      {/* =====================================================
          HERO SECTION
          ===================================================== */}

      <section className="hero-section">

        <div className="hero-content">

          {/* Main SmartFit introduction. */}
          <p className="hero-label">
            👕 VIRTUAL FITTING SYSTEM
          </p>

          <h1>
            Find the right fit
            <br />
            before you buy.
          </h1>

          <p className="hero-description">
            SmartFit helps online shoppers make better clothing
            decisions by using their body measurements and a
            personalized digital avatar to estimate how garments
            will fit.
          </p>

          {/* Primary actions. */}
          <div className="hero-actions">

            <Link
              to="/register"
              className="primary-button"
            >
              Get Started
            </Link>

            <a
              href="#how-it-works"
              className="secondary-button"
            >
              How It Works
            </a>

          </div>

        </div>


        {/* =================================================
            HERO VISUAL
            ================================================= */}

        <div className="hero-visual">

          <div className="avatar-placeholder">

            <span className="avatar-icon">
              🧍
            </span>

            <span>
              Your Digital Avatar
            </span>

          </div>

        </div>

      </section>


      {/* =====================================================
          HOW IT WORKS
          ===================================================== */}

      <section
        id="how-it-works"
        className="section"
      >

        <div className="section-heading">

          <p className="section-label">
            HOW IT WORKS
          </p>

          <h2>
            Your journey to a better fit
          </h2>

          <p>
            SmartFit simplifies the virtual fitting process
            into three main steps.
          </p>

        </div>


        <div className="steps-grid">

          {/* Step 1 */}
          <div className="step-card">

            <div className="step-number">
              01
            </div>

            <div className="step-icon">
              📹
            </div>

            <h3>
              Upload Your Video
            </h3>

            <p>
              Provide a short body video that allows SmartFit
              to estimate your body measurements.
            </p>

          </div>


          {/* Step 2 */}
          <div className="step-card">

            <div className="step-number">
              02
            </div>

            <div className="step-icon">
              🧍
            </div>

            <h3>
              Create Your Avatar
            </h3>

            <p>
              Your measurements are used to create a
              personalized digital representation of your body.
            </p>

          </div>


          {/* Step 3 */}
          <div className="step-card">

            <div className="step-number">
              03
            </div>

            <div className="step-icon">
              👕
            </div>

            <h3>
              Virtually Try Clothes
            </h3>

            <p>
              Select garments and receive fitting information
              and size recommendations before purchasing.
            </p>

          </div>

        </div>

      </section>


      {/* =====================================================
          BENEFITS
          ===================================================== */}

      <section className="benefits-section">

        <div className="benefits-content">

          <div className="section-heading">

            <p className="section-label">
              WHY SMARTFIT?
            </p>

            <h2>
              Shop with more confidence.
            </h2>

            <p>
              Online clothing shopping can make it difficult
              to know whether a garment will fit. SmartFit
              aims to reduce that uncertainty.
            </p>

          </div>


          <div className="benefits-list">

            <div className="benefit-item">

              <span>
                ✓
              </span>

              <div>
                <h3>
                  Better Size Selection
                </h3>

                <p>
                  Use personalized measurements to make more
                  informed clothing size decisions.
                </p>
              </div>

            </div>


            <div className="benefit-item">

              <span>
                ✓
              </span>

              <div>
                <h3>
                  Personalized Experience
                </h3>

                <p>
                  Your digital avatar provides a more
                  personalized representation of your body.
                </p>
              </div>

            </div>


            <div className="benefit-item">

              <span>
                ✓
              </span>

              <div>
                <h3>
                  Reduced Uncertainty
                </h3>

                <p>
                  Understand garment fit before committing
                  to an online purchase.
                </p>
              </div>

            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          FINAL CALL TO ACTION
          ===================================================== */}

      <section className="cta-section">

        <p className="section-label">
          GET STARTED
        </p>

        <h2>
          Ready to find your fit?
        </h2>

        <p>
          Create your SmartFit account and begin your
          personalized virtual fitting experience.
        </p>

        <Link
          to="/register"
          className="primary-button"
        >
          Create Account
        </Link>

      </section>

    </div>
  );
}


export default Home;