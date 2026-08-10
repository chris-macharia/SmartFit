/**
 * SmartFit Dashboard
 *
 * Main landing page for an authenticated SmartFit user.
 *
 * At this stage, the dashboard is frontend-only. The information
 * displayed here is static/mock data and will later be replaced
 * with information retrieved from the FastAPI backend.
 *
 * Main dashboard actions:
 * 1. Upload a body video.
 * 2. Manage the digital avatar.
 * 3. Browse available garments.
 * 4. Start a virtual fitting.
 */

import { Link } from "react-router-dom";


function Dashboard() {
  return (
    <main className="dashboard-page">

      {/* =====================================================
          DASHBOARD HEADER
          ===================================================== */}

      <section className="dashboard-header">

        <div>
          <p className="section-label">
            SMARTFIT DASHBOARD
          </p>

          <h1>
            Hello, User 👋
          </h1>

          <p className="dashboard-intro">
            Manage your measurements, digital avatar, garments,
            and virtual fitting experience from one place.
          </p>
        </div>

      </section>


      {/* =====================================================
          QUICK ACTIONS
          ===================================================== */}

      <section className="dashboard-section">

        <div className="dashboard-section-heading">

          <div>
            <p className="section-label">
              QUICK ACTIONS
            </p>

            <h2>
              What would you like to do?
            </h2>
          </div>

        </div>


        <div className="dashboard-actions">

          {/* =================================================
              UPLOAD VIDEO
              ================================================= */}

          <Link
            to="/upload-video"
            className="dashboard-card"
          >

            <div className="dashboard-card-icon">
              🎥
            </div>

            <h3>
              Upload Video
            </h3>

            <p>
              Upload a short body video so SmartFit can estimate
              your measurements and prepare your virtual fitting
              profile.
            </p>

            <span className="dashboard-card-link">
              Upload video →
            </span>

          </Link>


          {/* =================================================
              DIGITAL AVATAR
              ================================================= */}

          <Link
            to="/avatar"
            className="dashboard-card"
          >

            <div className="dashboard-card-icon">
              🧍
            </div>

            <h3>
              Digital Avatar
            </h3>

            <p>
              Create and manage the digital avatar used for
              your personalized virtual fitting experience.
            </p>

            <span className="dashboard-card-link">
              View avatar →
            </span>

          </Link>


          {/* =================================================
              GARMENTS
              ================================================= */}

          <Link
            to="/garments"
            className="dashboard-card"
          >

            <div className="dashboard-card-icon">
              👕
            </div>

            <h3>
              Browse Garments
            </h3>

            <p>
              Explore available clothing items and find garments
              that match your preferences.
            </p>

            <span className="dashboard-card-link">
              Browse garments →
            </span>

          </Link>


          {/* =================================================
              VIRTUAL FITTING
              ================================================= */}

          <Link
            to="/virtual-fitting"
            className="dashboard-card dashboard-card-featured"
          >

            <div className="dashboard-card-icon">
              🪞
            </div>

            <h3>
              Virtual Fitting
            </h3>

            <p>
              Try clothing virtually using your digital avatar
              and receive a personalized fit result.
            </p>

            <span className="dashboard-card-link">
              Start fitting →
            </span>

          </Link>

        </div>

      </section>


      {/* =====================================================
          PROFILE STATUS
          ===================================================== */}

      <section className="dashboard-section">

        <div className="dashboard-status-card">

          <div className="dashboard-status-content">

            <p className="section-label">
              PROFILE SETUP
            </p>

            <h2>
              Complete your SmartFit profile
            </h2>

            <p>
              Your virtual fitting experience becomes more
              accurate when your measurements and digital avatar
              are properly configured.
            </p>

          </div>


          {/* Temporary static progress indicator.
              This will later be calculated from backend data. */}

          <div className="dashboard-progress">

            <div className="dashboard-progress-header">

              <span>
                Setup progress
              </span>

              <strong>
                25%
              </strong>

            </div>


            <div className="progress-track">

              <div
                className="progress-bar"
                style={{ width: "25%" }}
              />

            </div>


            <p>
              Complete your profile to get started.
            </p>

          </div>

        </div>

      </section>


      {/* =====================================================
          HOW SMARTFIT WORKS
          ===================================================== */}

      <section className="dashboard-section">

        <div className="dashboard-section-heading">

          <p className="section-label">
            YOUR SMARTFIT JOURNEY
          </p>

          <h2>
            From measurements to better-fitting clothes
          </h2>

        </div>


        <div className="dashboard-journey">

          {/* Step 1 */}
          <div className="journey-step">

            <span className="journey-number">
              01
            </span>

            <h3>
              Measure
            </h3>

            <p>
              Upload a short body video so SmartFit can estimate
              your measurements.
            </p>

          </div>


          {/* Step 2 */}
          <div className="journey-step">

            <span className="journey-number">
              02
            </span>

            <h3>
              Create
            </h3>

            <p>
              SmartFit uses your information to create your
              personalized digital representation.
            </p>

          </div>


          {/* Step 3 */}
          <div className="journey-step">

            <span className="journey-number">
              03
            </span>

            <h3>
              Fit
            </h3>

            <p>
              Select a garment and see how it fits your
              personalized avatar.
            </p>

          </div>

        </div>

      </section>

    </main>
  );
}


export default Dashboard;

