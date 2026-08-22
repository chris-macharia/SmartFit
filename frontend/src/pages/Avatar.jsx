/**
 * SmartFit Generate Avatar Page
 *
 * This page represents Step 2 of the SmartFit body profile
 * creation process.
 *
 * Step 1:
 *
 *     Body Video
 *          ↓
 *     Body Measurement Extraction
 *
 * Step 2:
 *
 *     Retrieve Body Measurements
 *          ↓
 *     Generate Digital Avatar
 *
 * The page receives a video ID from the Upload Video page.
 * It then retrieves the latest video information from the
 * backend. The backend response contains the body measurement
 * generated from the uploaded video.
 *
 * Avatar generation is performed by the SmartFit backend.
 */

import {
  Link,
  useLocation,
  useNavigate,
} from "react-router-dom";

import {
  useEffect,
  useState,
} from "react";

import { getVideo } from "../services/videoService";
import { generateAvatar } from "../services/avatarService";


function GenerateAvatar() {

  // ============================================================
  // ROUTER
  // ============================================================

  const location = useLocation();

  const navigate = useNavigate();


  // ============================================================
  // VIDEO ID
  // ============================================================

  /*
   * The Upload Video page passes the completed video ID
   * through React Router state.
   *
   * Example:
   *
   *     navigate("/generate-avatar", {
   *         state: {
   *             videoId: video.video_id
   *         }
   *     });
   *
   * The video ID is then used to retrieve the latest
   * video information from the backend.
   */
  const videoId =
    location.state?.videoId || null;


  // ============================================================
  // COMPONENT STATE
  // ============================================================

  /*
   * Store the video returned by the backend.
   */
  const [video, setVideo] = useState(null);


  /*
   * Store the body measurement returned by the backend.
   */
  const [measurements, setMeasurements] = useState(null);


  /*
   * Track the initial loading state.
   */
  const [loading, setLoading] = useState(true);


  /*
   * Track avatar generation.
   */
  const [generating, setGenerating] = useState(false);


  /*
   * Store API errors.
   */
  const [error, setError] = useState("");


  // ============================================================
  // LOAD VIDEO AND MEASUREMENTS
  // ============================================================

  useEffect(() => {

    /*
     * There is no video ID available.
     *
     * This can happen if the user navigates directly to
     * /generate-avatar without first uploading a video.
     */
    if (!videoId) {

      setError(
        "No processed video was provided. Please upload and process your body video first."
      );

      setLoading(false);

      return;
    }


    /*
     * Retrieve the latest video information from the
     * backend.
     */
    async function loadVideo() {

      setLoading(true);
      setError("");


      try {

        const latestVideo =
          await getVideo(videoId);


        /*
         * Store the complete video response.
         */
        setVideo(latestVideo);


        /*
         * Make sure video processing has completed.
         */
        if (
          latestVideo.processing_status !==
          "completed"
        ) {

          setError(
            "Your body video has not finished processing yet. Please return to the upload page."
          );

          return;
        }


        /*
         * The backend includes the generated body
         * measurement in:
         *
         *     latestVideo.measurement
         */
        if (!latestVideo.measurement) {

          setError(
            "No body measurements were found for this video."
          );

          return;
        }


        /*
         * Store the measurement.
         */
        setMeasurements(
          latestVideo.measurement
        );

      } catch (err) {

        setError(
          err.message ||
          "Unable to retrieve your body measurements."
        );

      } finally {

        setLoading(false);
      }
    }


    loadVideo();

  }, [videoId]);


  // ============================================================
  // GENERATE AVATAR
  // ============================================================

  /**
   * Request digital avatar generation from the backend.
   */
  async function handleGenerateAvatar() {

    /*
     * Make sure the measurement exists.
     */
    if (!measurements?.measurement_id) {

      setError(
        "No body measurement record is available for avatar generation."
      );

      return;
    }


    setGenerating(true);
    setError("");


    try {

      /*
       * Send the measurement UUID to the existing
       * avatar generation endpoint.
       */
      const avatar =
        await generateAvatar(
          measurements.measurement_id
        );


      /*
       * Navigate to the Avatar page after successful
       * generation.
       *
       * Pass both the generated avatar and measurements
       * so the next page can display them immediately.
       */
      navigate(
        "/avatar",
        {
          state: {
            avatar,
            measurements,
            measurementId:
              measurements.measurement_id,
            videoId,
          },
        }
      );

    } catch (err) {

      setError(
        err.message ||
        "SmartFit could not generate your avatar."
      );

    } finally {

      setGenerating(false);
    }
  }


  // ============================================================
  // MEASUREMENT FORMATTER
  // ============================================================

  /**
   * Format a measurement value for display.
   *
   * @param {number|null} value
   * @returns {string}
   */
  function formatMeasurement(value) {

    if (
      value === null ||
      value === undefined
    ) {

      return "—";
    }


    if (typeof value === "number") {

      return `${value.toFixed(2)} cm`;
    }


    return value;
  }


  // ============================================================
  // RENDER - LOADING
  // ============================================================

  if (loading) {

    return (

      <main className="avatar-page">

        <section className="avatar-header">

          <Link
            to="/dashboard"
            className="back-link"
          >
            ← Back to Dashboard
          </Link>


          <p className="section-label">
            DIGITAL AVATAR
          </p>


          <h1>
            Preparing your avatar
          </h1>


          <p>
            SmartFit is retrieving your body measurements.
          </p>

        </section>


        <section className="avatar-workspace">

          <div className="avatar-preview-card">

            <div className="avatar-preview">

              <div className="avatar-placeholder">

                <div className="avatar-placeholder-icon">
                  🧍
                </div>


                <h2>
                  Loading your measurements...
                </h2>


                <p>
                  SmartFit is retrieving the measurements
                  generated from your body video.
                </p>


                <div className="avatar-loading">

                  <div className="avatar-spinner" />

                  <span>
                    Loading...
                  </span>

                </div>

              </div>

            </div>

          </div>

        </section>

      </main>
    );
  }


  // ============================================================
  // RENDER - NO VIDEO / ERROR
  // ============================================================

  /*
   * If there is no video ID, or if retrieving the video
   * or measurements failed, show the error state.
   *
   * The user is given a clear way to return to the
   * Upload Video page.
   */
  if (error) {

    return (

      <main className="avatar-page">

        <section className="avatar-header">

          <Link
            to="/dashboard"
            className="back-link"
          >
            ← Back to Dashboard
          </Link>


          <p className="section-label">
            DIGITAL AVATAR
          </p>


          <h1>
            Generate your SmartFit Avatar
          </h1>


          <p>
            Before generating your avatar, SmartFit needs
            a processed body video and its measurements.
          </p>

        </section>


        <section className="avatar-workspace">

          <div className="avatar-preview-card">

            <div className="avatar-preview">

              <div className="avatar-placeholder">

                <div className="avatar-placeholder-icon">
                  ⚠️
                </div>


                <h2>
                  Unable to continue
                </h2>


                <div
                  className="form-message error-message"
                  role="alert"
                >
                  {error}
                </div>

              </div>

            </div>


            {/* =================================================
                RETURN TO UPLOAD VIDEO
                ================================================= */}

            <Link
              to="/upload-video"
              className="primary-button avatar-generate-button"
            >
              Go to Upload Video
            </Link>

          </div>

        </section>


        {/* =====================================================
            EXPLANATION
            ===================================================== */}

        <section className="avatar-explanation">

          <div>

            <p className="section-label">
              SMARTFIT PROFILE
            </p>


            <h2>
              Start with your body video.
            </h2>

          </div>


          <div className="avatar-explanation-text">

            <p>
              SmartFit needs a processed body video before
              your body measurements can be retrieved.
            </p>


            <p>
              Upload your video and allow SmartFit to finish
              extracting your measurements before returning
              here to generate your digital avatar.
            </p>

          </div>

        </section>

      </main>
    );
  }


  // ============================================================
  // RENDER - MAIN PAGE
  // ============================================================

  return (

    <main className="avatar-page">

      {/* =====================================================
          PAGE HEADER
          ===================================================== */}

      <section className="avatar-header">

        <Link
          to="/dashboard"
          className="back-link"
        >
          ← Back to Dashboard
        </Link>


        <p className="section-label">
          DIGITAL AVATAR
        </p>


        <h1>
          Generate your SmartFit Avatar
        </h1>


        <p>
          Your body measurements have been extracted from
          your uploaded video. Review them below before
          generating your digital avatar.
        </p>

      </section>


      {/* =====================================================
          WORKSPACE
          ===================================================== */}

      {measurements && (

        <section className="avatar-workspace">

          {/* =================================================
              MEASUREMENT SUMMARY
              ================================================= */}

          <div className="avatar-info-card">

            <p className="section-label">
              BODY MEASUREMENTS
            </p>


            <h2>
              Your measurements
            </h2>


            <p className="avatar-measurement-intro">
              These measurements were extracted from your
              uploaded body video and will be used to
              generate your personalized digital avatar.
            </p>


            <div className="measurement-grid">

              {/* Height */}

              <div className="measurement-item">

                <span>
                  Height
                </span>


                <strong>
                  {formatMeasurement(
                    measurements.height
                  )}
                </strong>

              </div>


              {/* Chest */}

              <div className="measurement-item">

                <span>
                  Chest
                </span>


                <strong>
                  {formatMeasurement(
                    measurements.chest
                  )}
                </strong>

              </div>


              {/* Waist */}

              <div className="measurement-item">

                <span>
                  Waist
                </span>


                <strong>
                  {formatMeasurement(
                    measurements.waist
                  )}
                </strong>

              </div>


              {/* Hips */}

              <div className="measurement-item">

                <span>
                  Hips
                </span>


                <strong>
                  {formatMeasurement(
                    measurements.hips
                  )}
                </strong>

              </div>


              {/* Shoulder */}

              <div className="measurement-item">

                <span>
                  Shoulder Width
                </span>


                <strong>
                  {formatMeasurement(
                    measurements.shoulder_width
                  )}
                </strong>

              </div>


              {/* Inseam */}

              <div className="measurement-item">

                <span>
                  Inseam
                </span>


                <strong>
                  {formatMeasurement(
                    measurements.inseam
                  )}
                </strong>

              </div>

            </div>


            {/* =================================================
                CONFIDENCE
                ================================================= */}

            <div className="avatar-status-list">

              <div className="avatar-status-item">

                <span>
                  Measurement confidence
                </span>


                <strong className="status-complete">

                  {typeof measurements.confidence_score ===
                    "number"
                    ? `${(
                        measurements.confidence_score *
                        100
                      ).toFixed(0)}%`
                    : "Available"}

                </strong>

              </div>


              <div className="avatar-status-item">

                <span>
                  Processing version
                </span>


                <strong className="status-complete">

                  {measurements.processing_version}

                </strong>

              </div>

            </div>

          </div>


          {/* =================================================
              GENERATE AVATAR
              ================================================= */}

          <div className="avatar-preview-card">

            <div className="avatar-preview">

              <div className="avatar-placeholder">

                <div className="avatar-placeholder-icon">
                  🧍
                </div>


                <h2>
                  Ready to create your avatar
                </h2>


                <p>
                  SmartFit will use your extracted body
                  measurements to create your personalized
                  digital avatar.
                </p>


                {generating && (

                  <div className="avatar-loading">

                    <div className="avatar-spinner" />


                    <span>
                      Creating your avatar...
                    </span>

                  </div>

                )}

              </div>

            </div>


            <button
              type="button"
              className="primary-button avatar-generate-button"
              onClick={handleGenerateAvatar}
              disabled={generating}
            >

              {generating
                ? "Creating Avatar..."
                : "Generate Avatar"}

            </button>

          </div>

        </section>

      )}


      {/* =====================================================
          EXPLANATION
          ===================================================== */}

      <section className="avatar-explanation">

        <div>

          <p className="section-label">
            NEXT STEP
          </p>


          <h2>
            Your measurements power your digital avatar.
          </h2>

        </div>


        <div className="avatar-explanation-text">

          <p>
            SmartFit first extracts your body measurements
            from the uploaded video.
          </p>


          <p>
            These measurements are stored in your SmartFit
            profile and then passed to the avatar generation
            system.
          </p>


          <p>
            Once your avatar has been generated, you can
            continue to the virtual fitting experience.
          </p>

        </div>

      </section>

    </main>
  );
}


export default GenerateAvatar;