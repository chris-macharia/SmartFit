/**
 * SmartFit Dashboard
 *
 * This page is the main authenticated landing page for
 * SmartFit users.
 *
 * Responsibilities:
 *
 * - Welcome the authenticated user.
 * - Provide access to the main SmartFit features.
 * - Provide navigation to video upload and avatar features.
 *
 * The authenticated user's information comes from
 * AuthContext rather than being hard-coded.
 */

import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";


function Dashboard() {


  /*
   * ---------------------------------------------------------
   * AUTHENTICATED USER
   * ---------------------------------------------------------
   *
   * Retrieve the currently authenticated user from the
   * centralized authentication context.
   *
   * AuthContext obtains this information from:
   *
   * GET /api/users/me
   *
   * after validating the JWT stored during login.
   */
  const {
    user,
  } = useAuth();


  /*
   * ---------------------------------------------------------
   * USER DISPLAY NAME
   * ---------------------------------------------------------
   *
   * Normally user.full_name will always be available.
   *
   * The fallback prevents the page from displaying
   * "undefined" if the user object has not yet been
   * populated for some reason.
   */
  const displayName =
    user?.full_name || "User";


  return (
    <main className="dashboard-page">


      {/* =================================================
          DASHBOARD HEADER
          ================================================= */}

      <section className="dashboard-header">


        <div className="dashboard-heading">


          <p className="section-label">
            SMARTFIT DASHBOARD
          </p>


          {/*
           * Display the authenticated user's actual name
           * instead of the previous static "Hello user".
           */}
          <h1>
            Hello, {displayName}
          </h1>


          <p>
            Welcome to your personalized virtual fitting
            experience.
          </p>


        </div>


      </section>


      {/* =================================================
          MAIN DASHBOARD FEATURES
          ================================================= */}

      <section className="dashboard-section">


        <div className="section-heading">


          <p className="section-label">
            SMARTFIT FEATURES
          </p>


          <h2>
            What would you like to do?
          </h2>


          <p>
            Choose a SmartFit feature to continue.
          </p>


        </div>


        {/* =================================================
            FEATURE CARDS
            ================================================= */}

        <div className="dashboard-grid">


          {/* ---------------------------------------------
              UPLOAD VIDEO
              --------------------------------------------- */}

          <Link
            to="/upload-video"
            className="dashboard-card"
          >


            <div className="dashboard-card-icon">
              🎥
            </div>


            <div className="dashboard-card-content">


              <h3>
                Upload Video
              </h3>


              <p>
                Upload a short video to begin estimating
                your body measurements.
              </p>


            </div>


            <span className="dashboard-card-action">
              Get Started →
            </span>


          </Link>


          {/* ---------------------------------------------
              VIEW AVATAR
              --------------------------------------------- */}

          <Link
            to="/avatar"
            className="dashboard-card"
          >


            <div className="dashboard-card-icon">
              🧍
            </div>


            <div className="dashboard-card-content">


              <h3>
                View Avatar
              </h3>


              <p>
                View your personalized digital avatar
                generated from your measurements.
              </p>


            </div>


            <span className="dashboard-card-action">
              View Avatar →
            </span>


          </Link>


          {/* ---------------------------------------------
              VIRTUAL FITTING
              --------------------------------------------- */}

          <div
            className="dashboard-card dashboard-card-disabled"
          >


            <div className="dashboard-card-icon">
              👕
            </div>


            <div className="dashboard-card-content">


              <h3>
                Virtual Fitting
              </h3>


              <p>
                Try garments virtually using your
                personalized avatar.
              </p>


            </div>


            <span className="dashboard-card-action">
              Coming Soon
            </span>


          </div>


          {/* ---------------------------------------------
              SIZE RECOMMENDATION
              --------------------------------------------- */}

          <div
            className="dashboard-card dashboard-card-disabled"
          >


            <div className="dashboard-card-icon">
              📏
            </div>


            <div className="dashboard-card-content">


              <h3>
                Size Recommendation
              </h3>


              <p>
                Receive clothing size recommendations
                based on your measurements.
              </p>


            </div>


            <span className="dashboard-card-action">
              Coming Soon
            </span>


          </div>


        </div>


      </section>


    </main>
  );
}


export default Dashboard;