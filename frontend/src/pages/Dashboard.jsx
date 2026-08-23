/**
 * SmartFit Dashboard
 *
 * This page is the main authenticated landing page for
 * SmartFit users.
 *
 * Dashboard content is determined by the authenticated
 * user's account role.
 *
 * Customer:
 * - Upload Video
 * - View Avatar
 * - Virtual Fitting
 * - Size Recommendation
 *
 * Retailer:
 * - Manage Garments
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
   * populated.
   */
  const displayName =
    user?.full_name || "User";


  /*
   * ---------------------------------------------------------
   * USER ROLE
   * ---------------------------------------------------------
   *
   * The backend user model stores the account role.
   *
   * Retailers receive a different dashboard from customers
   * because retailers manage garments rather than uploading
   * body videos and generating avatars.
   */
  const isRetailer =
    user?.role === "retailer";


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


          <h1>
            Hello, {displayName}
          </h1>


          <p>
            {isRetailer
              ? "Manage your garments for the SmartFit virtual fitting experience."
              : "Welcome to your personalized virtual fitting experience."}
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
            {isRetailer
              ? "Manage your garments"
              : "What would you like to do?"}
          </h2>


          <p>
            {isRetailer
              ? "Register and manage the garments available for virtual fitting."
              : "Choose a SmartFit feature to continue."}
          </p>


        </div>


        {/* =================================================
            RETAILER DASHBOARD
            ================================================= */}

        {isRetailer ? (

          <div className="dashboard-grid">


            {/* ---------------------------------------------
                MANAGE GARMENTS
                --------------------------------------------- */}

            <Link
              to="/garments"
              className="dashboard-card"
            >


              <div className="dashboard-card-icon">
                👕
              </div>


              <div className="dashboard-card-content">


                <h3>
                  Upload Garments
                </h3>


                <p>
                  Register new garments and manage the
                  measurements of garments you have uploaded.
                </p>


              </div>


              <span className="dashboard-card-action">
                Upload Garments →
              </span>


            </Link>


          </div>

        ) : (


          /* =================================================
             CUSTOMER DASHBOARD
             ================================================= */

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

        )}


      </section>


    </main>
  );
}


export default Dashboard;