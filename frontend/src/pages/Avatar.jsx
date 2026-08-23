/**
 * SmartFit Avatar Page
 *
 * Displays the generated SmartFit digital avatar as an
 * interactive 3D model.
 *
 * Workflow:
 *
 *     GenerateAvatar.jsx
 *            ↓
 *       generateAvatar()
 *            ↓
 *       avatar_id
 *            ↓
 *         Avatar.jsx
 *            ↓
 *       getAvatarFile()
 *            ↓
 *          GLB Blob
 *            ↓
 *       Browser Object URL
 *            ↓
 *       React Three Fiber
 *            ↓
 *       Interactive Avatar
 */

import {
  Link,
  useLocation,
  useNavigate,
} from "react-router-dom";

import {
  Suspense,
  useEffect,
  useState,
} from "react";

import {
  Canvas,
} from "@react-three/fiber";

import {
  OrbitControls,
  useGLTF,
} from "@react-three/drei";

import {
  getAvatarFile,
} from "../services/avatarService";


// ============================================================
// AVATAR MODEL
// ============================================================

/**
 * Load and render the GLB avatar.
 *
 * @param {Object} props
 * @param {string} props.url - Browser object URL of the GLB.
 */
function AvatarModel({ url }) {

  const { scene } = useGLTF(url);


  return (
    <primitive
      object={scene}
      scale={1}
      position={[0, 0, 0]}
    />
  );
}


// ============================================================
// MODEL LOADING FALLBACK
// ============================================================

function ModelLoading() {

  return (

    <div className="avatar-viewer-message">

      <div className="avatar-spinner" />

      <p>
        Loading your 3D avatar...
      </p>

    </div>
  );
}


// ============================================================
// AVATAR PAGE
// ============================================================

function Avatar() {

  // ============================================================
  // ROUTER
  // ============================================================

  const location = useLocation();

  const navigate = useNavigate();


  // ============================================================
  // ROUTER STATE
  // ============================================================

  /*
   * GenerateAvatar.jsx passes the generated avatar through
   * React Router state.
   */
  const avatar =
    location.state?.avatar || null;


  /*
   * Body measurements are also passed through so they can
   * be displayed alongside the avatar.
   */
  const measurements =
    location.state?.measurements || null;


  /*
   * Video ID is preserved for future use.
   */
  const videoId =
    location.state?.videoId || null;


  // ============================================================
  // COMPONENT STATE
  // ============================================================

  /*
   * Browser object URL pointing to the downloaded GLB file.
   */
  const [modelUrl, setModelUrl] =
    useState(null);


  /*
   * Track whether the GLB is currently being downloaded.
   */
  const [loading, setLoading] =
    useState(true);


  /*
   * Store any loading error.
   */
  const [error, setError] =
    useState("");


  // ============================================================
  // DEBUG INFORMATION
  // ============================================================

  /*
   * These logs make the avatar workflow visible during
   * development.
   *
   * They can be removed once everything is confirmed working.
   */

  useEffect(() => {

    console.log(
      "SmartFit Avatar Page loaded."
    );

    console.log(
      "Avatar:",
      avatar
    );

    console.log(
      "Avatar ID:",
      avatar?.avatar_id
    );

    console.log(
      "Measurements:",
      measurements
    );

    console.log(
      "Video ID:",
      videoId
    );

  }, [
    avatar,
    measurements,
    videoId,
  ]);


  // ============================================================
  // LOAD AVATAR GLB
  // ============================================================

  useEffect(() => {

    /*
     * Do not attempt to retrieve the GLB unless an
     * avatar ID was actually supplied.
     */
    if (!avatar?.avatar_id) {

      console.error(
        "SmartFit Avatar: No avatar_id was provided."
      );

      setError(
        "No generated avatar was provided. Please generate your avatar first."
      );

      setLoading(false);

      return;
    }


    let objectUrl = null;

    let cancelled = false;


    async function loadAvatar() {

      setLoading(true);

      setError("");

      setModelUrl(null);


      try {

        console.log(
          "SmartFit Avatar: Requesting GLB file..."
        );

        console.log(
          "Avatar ID:",
          avatar.avatar_id
        );


        /*
         * Call the authenticated avatar file endpoint.
         *
         * This should result in:
         *
         * GET /api/avatars/{avatar_id}/file
         */
        objectUrl =
          await getAvatarFile(
            avatar.avatar_id
          );


        console.log(
          "SmartFit Avatar: GLB file received."
        );

        console.log(
          "Object URL:",
          objectUrl
        );


        /*
         * The component may have been unmounted while
         * the request was running.
         */
        if (cancelled) {

          if (objectUrl) {

            URL.revokeObjectURL(
              objectUrl
            );
          }

          return;
        }


        /*
         * Store the temporary browser URL.
         */
        setModelUrl(
          objectUrl
        );

      } catch (err) {

        console.error(
          "SmartFit Avatar: Failed to load GLB.",
          err
        );


        if (!cancelled) {

          setError(
            err.message ||
            "Unable to load your generated avatar."
          );
        }

      } finally {

        if (!cancelled) {

          setLoading(false);
        }
      }
    }


    loadAvatar();


    // ----------------------------------------------------------
    // CLEANUP
    // ----------------------------------------------------------

    return () => {

      cancelled = true;


      /*
       * Release the browser object URL when the component
       * is unmounted or when another avatar is loaded.
       */
      if (objectUrl) {

        console.log(
          "SmartFit Avatar: Releasing GLB object URL."
        );

        URL.revokeObjectURL(
          objectUrl
        );
      }
    };

  }, [
    avatar?.avatar_id,
  ]);


  // ============================================================
  // NO AVATAR
  // ============================================================

  if (!avatar?.avatar_id) {

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
            No Avatar Available
          </h1>


          <p>
            Generate your SmartFit avatar before opening
            the 3D viewer.
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
                  Avatar not found
                </h2>


                <p>
                  No generated avatar was provided to this page.
                </p>

              </div>

            </div>


            <button
              type="button"
              className="primary-button avatar-generate-button"
              onClick={() =>
                navigate(
                  "/generate-avatar"
                )
              }
            >
              Generate Avatar
            </button>

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
            Your SmartFit Avatar
          </h1>


          <p>
            The avatar was generated, but SmartFit could
            not load the 3D model.
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
                  Unable to load avatar
                </h2>


                <div
                  className="form-message error-message"
                  role="alert"
                >
                  {error}
                </div>

              </div>

            </div>


            <div className="avatar-error-actions">

              <button
                type="button"
                className="primary-button"
                onClick={() =>
                  window.location.reload()
                }
              >
                Try Again
              </button>


              <button
                type="button"
                className="secondary-button"
                onClick={() =>
                  navigate(
                    "/generate-avatar",
                    {
                      state: {
                        videoId,
                      },
                    }
                  )
                }
              >
                Back to Avatar Generation
              </button>

            </div>

          </div>

        </section>

      </main>
    );
  }


  // ============================================================
  // MAIN AVATAR VIEWER
  // ============================================================

  return (

    <main className="avatar-page">

      {/* ======================================================
          PAGE HEADER
          ====================================================== */}

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
          Your SmartFit Avatar
        </h1>


        <p>
          Your personalized digital avatar has been
          generated from your body measurements.
        </p>

      </section>


      {/* ======================================================
          AVATAR WORKSPACE
          ====================================================== */}

      <section className="avatar-workspace">

        {/* ====================================================
            3D VIEWER
            ==================================================== */}

        <div className="avatar-preview-card">

          <div
            className="avatar-preview avatar-3d-preview"
          >

            {/* =================================================
                GLB DOWNLOAD LOADING
                ================================================= */}

            {loading && (

              <ModelLoading />

            )}


            {/* =================================================
                THREE.JS VIEWER
                ================================================= */}

            {!loading && modelUrl && (

              <Canvas
                camera={{
                  position: [
                    0,
                    1.2,
                    3,
                  ],
                  fov: 45,
                }}
              >

                {/* ==========================================
                    LIGHTING
                    ========================================== */}

                <ambientLight
                  intensity={1.5}
                />


                <directionalLight
                  position={[
                    5,
                    5,
                    5,
                  ]}
                  intensity={2}
                />


                <directionalLight
                  position={[
                    -5,
                    3,
                    2,
                  ]}
                  intensity={1}
                />


                {/* ==========================================
                    AVATAR MODEL
                    ========================================== */}

                <Suspense
                  fallback={null}
                >

                  <AvatarModel
                    url={modelUrl}
                  />

                </Suspense>


                {/* ==========================================
                    CAMERA CONTROLS
                    ========================================== */}

                <OrbitControls
                  enablePan={false}
                  minDistance={1.5}
                  maxDistance={5}
                  target={[
                    0,
                    1,
                    0,
                  ]}
                />

              </Canvas>

            )}

          </div>


          {/* =================================================
              VIEWER INSTRUCTIONS
              ================================================= */}

          {!loading && modelUrl && (

            <div className="avatar-viewer-controls">

              <span>
                Drag to rotate
              </span>


              <span>
                Scroll to zoom
              </span>

            </div>

          )}

        </div>


        {/* ====================================================
            AVATAR INFORMATION
            ==================================================== */}

        <div className="avatar-info-card">

          <p className="section-label">
            SMARTFIT AVATAR
          </p>


          <h2>
            Your digital body profile
          </h2>


          <p className="avatar-measurement-intro">
            This avatar was generated using the body
            measurements extracted from your uploaded
            body video.
          </p>


          {/* ==================================================
              MEASUREMENTS
              ================================================== */}

          {measurements && (

            <div className="measurement-grid">

              {/* Height */}

              <div className="measurement-item">

                <span>
                  Height
                </span>


                <strong>

                  {typeof measurements.height ===
                    "number"
                    ? `${measurements.height.toFixed(
                        2
                      )} cm`
                    : "—"}

                </strong>

              </div>


              {/* Shoulder Width */}

              <div className="measurement-item">

                <span>
                  Shoulder Width
                </span>


                <strong>

                  {typeof measurements.shoulder_width ===
                    "number"
                    ? `${measurements.shoulder_width.toFixed(
                        2
                      )} cm`
                    : "—"}

                </strong>

              </div>


              {/* Inseam */}

              <div className="measurement-item">

                <span>
                  Inseam
                </span>


                <strong>

                  {typeof measurements.inseam ===
                    "number"
                    ? `${measurements.inseam.toFixed(
                        2
                      )} cm`
                    : "—"}

                </strong>

              </div>


              {/* Confidence */}

              <div className="measurement-item">

                <span>
                  Confidence
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

            </div>

          )}


          {/* ==================================================
              AVATAR STATUS
              ================================================== */}

          <div className="avatar-status-list">

            <div className="avatar-status-item">

              <span>
                Avatar status
              </span>


              <strong className="status-complete">
                Generated
              </strong>

            </div>


            <div className="avatar-status-item">

              <span>
                Avatar ID
              </span>


              <strong>
                {avatar.avatar_id}
              </strong>

            </div>

          </div>

        </div>

      </section>


      {/* ======================================================
          NEXT STEP
          ====================================================== */}

      <section className="avatar-explanation">

        <div>

          <p className="section-label">
            NEXT STEP
          </p>


          <h2>
            Your avatar is ready for virtual fitting.
          </h2>

        </div>


        <div className="avatar-explanation-text">

          <p>
            Your SmartFit avatar represents the body
            measurements extracted from your uploaded video.
          </p>


          <p>
            The next stage of SmartFit can use this avatar
            when evaluating how garments fit your body.
          </p>

        </div>

      </section>

    </main>
  );
}


export default Avatar;