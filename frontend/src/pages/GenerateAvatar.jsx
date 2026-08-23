/**
 * SmartFit Generate Avatar Page
 *
 * Responsible for generating a digital avatar from the
 * body measurements extracted from a processed video.
 *
 * Workflow:
 *
 *     UploadVideo.jsx
 *            ↓
 *        videoId
 *            ↓
 *       getVideo()
 *            ↓
 *     BodyMeasurement
 *            ↓
 *     generateAvatar()
 *            ↓
 *        Avatar
 *            ↓
 *       Avatar.jsx
 *
 * This page does NOT render the 3D model.
 *
 * Avatar.jsx is responsible for downloading and displaying
 * the generated GLB model.
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

import {
  getVideo,
} from "../services/videoService";

import {
  generateAvatar,
} from "../services/avatarService";


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
   * UploadVideo.jsx passes the completed video ID through
   * React Router state.
   */
  const videoId =
    location.state?.videoId || null;


  // ============================================================
  // COMPONENT STATE
  // ============================================================

  const [video, setVideo] =
    useState(null);


  const [measurements, setMeasurements] =
    useState(null);


  const [loading, setLoading] =
    useState(true);


  const [generating, setGenerating] =
    useState(false);


  const [error, setError] =
    useState("");


  // ============================================================
  // LOAD VIDEO AND MEASUREMENTS
  // ============================================================

  useEffect(() => {

    if (!videoId) {

      setError(
        "No processed video was provided. Please upload and process your body video first."
      );

      setLoading(false);

      return;
    }


    async function loadVideo() {

      setLoading(true);
      setError("");


      try {

        const latestVideo =
          await getVideo(videoId);


        setVideo(latestVideo);


        // ------------------------------------------------------
        // Verify processing completed.
        // ------------------------------------------------------

        if (
          latestVideo.processing_status !==
          "completed"
        ) {

          throw new Error(
            "Your body video has not finished processing yet. Please return to the upload page."
          );
        }


        // ------------------------------------------------------
        // Retrieve measurement.
        // ------------------------------------------------------

        if (!latestVideo.measurement) {

          throw new Error(
            "No body measurements were found for this video."
          );
        }


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

  async function handleGenerateAvatar() {

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
       * Generate the avatar using the measurement UUID.
       */
      const avatar =
        await generateAvatar(
          measurements.measurement_id
        );


      /*
       * Make sure the backend actually returned an
       * avatar ID.
       */
      if (!avatar?.avatar_id) {

        throw new Error(
          "The avatar was generated, but the backend did not return an avatar ID."
        );
      }


      /*
       * Navigate to the dedicated Avatar viewer.
       *
       * Avatar.jsx will use the avatar ID to retrieve
       * the generated GLB file.
       */
      navigate(
        "/avatar",
        {
          state: {
            avatar,
            measurements,
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
  // FORMAT MEASUREMENT
  // ============================================================

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
  // LOADING
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
  // ERROR
  // ============================================================

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
            Unable to continue
          </h1>


          <p>
            SmartFit could not prepare your avatar.
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
                  Something went wrong
                </h2>


                <div
                  className="form-message error-message"
                  role="alert"
                >
                  {error}
                </div>

              </div>

            </div>


            <Link
              to="/upload-video"
              className="primary-button avatar-generate-button"
            >
              Return to Upload Video
            </Link>

          </div>

        </section>

      </main>
    );
  }


  // ============================================================
  // MAIN PAGE
  // ============================================================

  return (

    <main className="avatar-page">

      {/* ======================================================
          HEADER
          ====================================================== */}

      <section className="avatar-header">

        <Link
          to="/upload-video"
          className="back-link"
        >
          ← Back to Upload Video
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


      {/* ======================================================
          WORKSPACE
          ====================================================== */}

      <section className="avatar-workspace">

        {/* ====================================================
            MEASUREMENTS
            ==================================================== */}

        <div className="avatar-info-card">

          <p className="section-label">
            BODY MEASUREMENTS
          </p>


          <h2>
            Your measurements
          </h2>


          <p className="avatar-measurement-intro">
            These measurements were extracted from your
            uploaded body video and will be used to generate
            your personalized digital avatar.
          </p>


          <div className="measurement-grid">

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


          {/* ==================================================
              CONFIDENCE
              ================================================== */}

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
                    ).toFixed(1)}%`
                  : "Available"}

              </strong>

            </div>


            <div className="avatar-status-item">

              <span>
                Processing version
              </span>


              <strong className="status-complete">

                {measurements.processing_version ||
                  "Available"}

              </strong>

            </div>

          </div>

        </div>


        {/* ====================================================
            GENERATE
            ==================================================== */}

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


      {/* ======================================================
          EXPLANATION
          ====================================================== */}

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
            These measurements are then passed to the avatar
            generation system.
          </p>


          <p>
            Once generation is complete, you will be taken
            to your interactive 3D avatar.
          </p>

        </div>

      </section>

    </main>
  );
}


export default GenerateAvatar;