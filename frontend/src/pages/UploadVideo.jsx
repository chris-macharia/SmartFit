/**
 * SmartFit Upload Video Page
 *
 * This page provides the interface for uploading a user's
 * body video for the SmartFit virtual fitting process.
 *
 * Current frontend responsibilities:
 *
 * 1. Allow the user to select a video file.
 * 2. Validate the selected file.
 * 3. Display a video preview.
 * 4. Display the selected file's information.
 * 5. Allow the user to remove or replace the video.
 * 6. Upload the video to the SmartFit FastAPI backend.
 *
 * Backend workflow:
 *
 *     Video Upload
 *          ↓
 *     FastAPI API
 *          ↓
 *     PostgreSQL Video Record
 *          ↓
 *     Computer Vision Processing
 *          ↓
 *     Body Measurements
 *          ↓
 *     Digital Avatar
 */

import { useRef, useState } from "react";
import { Link } from "react-router-dom";

import { uploadVideo } from "../services/videoService";


function UploadVideo() {
  // ============================================================
  // FILE INPUT REFERENCE
  // ============================================================

  // Reference to the hidden file input.
  //
  // This allows the custom upload interface to trigger
  // the browser's native file selection dialog.
  const fileInputRef = useRef(null);


  // ============================================================
  // COMPONENT STATE
  // ============================================================

  // Store the selected video file.
  const [selectedFile, setSelectedFile] = useState(null);

  // Store the user's declared height. SmartFit uses this value as the
  // real-world scale reference for the initial measurement estimates.
  const [userHeightCm, setUserHeightCm] = useState("");

  // Store the temporary browser URL used to preview the video.
  const [previewUrl, setPreviewUrl] = useState("");

  // Store validation or API errors.
  const [error, setError] = useState("");

  // Track whether the upload request is currently running.
  const [uploading, setUploading] = useState(false);

  // Store upload progress.
  //
  // At this stage, the Fetch API does not provide upload
  // progress events, so this is used for the upload state.
  // Real upload progress can be added later if required.
  const [uploadProgress, setUploadProgress] = useState(0);

  // Store a successful upload message.
  const [success, setSuccess] = useState("");

  // Store the video returned by the backend.
  //
  // This is useful during development because it allows us
  // to confirm that FastAPI successfully created the video
  // database record.
  const [uploadedVideo, setUploadedVideo] = useState(null);


  // ============================================================
  // FILE CONFIGURATION
  // ============================================================

  /**
   * Maximum accepted video size.
   *
   * Five hundred megabytes accommodates realistic short body videos,
   * particularly those recorded by modern mobile phones.
   *
   * The backend should also enforce its own upload limits.
   */
  const MAX_FILE_SIZE = 500 * 1024 * 1024;


  /**
   * Accepted video formats.
   *
   * These match the formats accepted by the FastAPI
   * video endpoint.
   */
  const ACCEPTED_VIDEO_TYPES = [
    "video/mp4",
    "video/webm",
    "video/quicktime",
  ];


  // ============================================================
  // FILE SELECTION
  // ============================================================

  /**
   * Validate and store a selected video file.
   *
   * @param {File} file - Selected video file.
   */
  function handleFileSelect(file) {
    // Clear previous feedback.
    setError("");
    setSuccess("");
    setUploadedVideo(null);
    setUploadProgress(0);


    // Make sure a file was actually selected.
    if (!file) {
      return;
    }


    // ----------------------------------------------------------
    // Validate file type
    // ----------------------------------------------------------

    if (!ACCEPTED_VIDEO_TYPES.includes(file.type)) {
      setError(
        "Please select an MP4, WebM, or MOV video file."
      );

      return;
    }


    // ----------------------------------------------------------
    // Validate file size
    // ----------------------------------------------------------

    if (file.size > MAX_FILE_SIZE) {
      setError(
        "The selected video is too large. Please choose a video smaller than 50 MB."
      );

      return;
    }


    // ----------------------------------------------------------
    // Release previous preview URL
    // ----------------------------------------------------------

    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }


    // ----------------------------------------------------------
    // Create new preview URL
    // ----------------------------------------------------------

    const videoUrl = URL.createObjectURL(file);


    // Store the selected file and preview.
    setSelectedFile(file);
    setPreviewUrl(videoUrl);
  }


  // ============================================================
  // FILE INPUT HANDLER
  // ============================================================

  /**
   * Handle selection through the standard file picker.
   */
  function handleInputChange(event) {
    const file = event.target.files[0];

    handleFileSelect(file);
  }


  // ============================================================
  // OPEN FILE PICKER
  // ============================================================

  /**
   * Open the browser's native file selection dialog.
   */
  function openFilePicker() {
    fileInputRef.current?.click();
  }


  // ============================================================
  // DRAG AND DROP
  // ============================================================

  /**
   * Handle drag-and-drop uploads.
   */
  function handleDrop(event) {
    event.preventDefault();

    const file = event.dataTransfer.files[0];

    handleFileSelect(file);
  }


  /**
   * Prevent the browser from opening the dropped file directly.
   */
  function handleDragOver(event) {
    event.preventDefault();
  }


  // ============================================================
  // REMOVE SELECTED VIDEO
  // ============================================================

  /**
   * Remove the currently selected video from the page.
   *
   * This only removes the selected local file.
   *
   * It does NOT delete a video that has already been
   * uploaded to the backend.
   */
  function removeVideo() {
    // Release the temporary browser URL.
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }


    // Reset the upload state.
    setSelectedFile(null);
    setPreviewUrl("");
    setError("");
    setSuccess("");
    setUploadProgress(0);
    setUploadedVideo(null);


    // Reset the file input so the same file can be
    // selected again if necessary.
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }


  // ============================================================
  // UPLOAD VIDEO
  // ============================================================

  /**
   * Upload the selected video to the SmartFit backend.
   *
   * The request is handled by videoService.js, which sends
   * the file to:
   *
   *     POST /api/videos/
   *
   * The backend authenticates the user using the JWT.
   */
  async function handleUpload() {
    // Make sure a file has been selected.
    if (!selectedFile) {
      setError("Please select a video before continuing.");

      return;
    }


    // A camera video does not contain a dependable centimetre scale by
    // itself, so height is required before the backend can process it.
    const parsedHeight = Number(userHeightCm);

    if (!Number.isFinite(parsedHeight) || parsedHeight < 100 || parsedHeight > 250) {
      setError("Please enter your height between 100 cm and 250 cm.");

      return;
    }


    // Clear previous feedback.
    setError("");
    setSuccess("");
    setUploadedVideo(null);


    // Begin upload state.
    setUploading(true);
    setUploadProgress(0);


    try {
      // --------------------------------------------------------
      // Send video to FastAPI
      // --------------------------------------------------------

      const video = await uploadVideo(
        selectedFile,
        parsedHeight
      );


      // --------------------------------------------------------
      // Store backend response
      // --------------------------------------------------------

      setUploadedVideo(video);


      // The request has completed successfully.
      setUploadProgress(100);


      // Display success message.
      setSuccess(
        "Video uploaded successfully. Processing will begin shortly."
      );


      // --------------------------------------------------------
      // Release local preview
      // --------------------------------------------------------

      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }


      // --------------------------------------------------------
      // Clear selected file
      // --------------------------------------------------------

      setSelectedFile(null);
      setPreviewUrl("");


      // Reset the file input.
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

    } catch (err) {
      // --------------------------------------------------------
      // Handle API error
      // --------------------------------------------------------

      setError(
        err.message ||
        "An error occurred while uploading the video."
      );

    } finally {
      // Upload request has finished regardless of success
      // or failure.
      setUploading(false);
    }
  }


  // ============================================================
  // FORMAT FILE SIZE
  // ============================================================

  /**
   * Format the file size into a readable value.
   *
   * @param {number} bytes - File size in bytes.
   * @returns {string} Formatted file size.
   */
  function formatFileSize(bytes) {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  }


  // ============================================================
  // RENDER
  // ============================================================

  return (
    <main className="upload-page">

      {/* =====================================================
          PAGE HEADER
          ===================================================== */}

      <section className="upload-header">

        <Link
          to="/dashboard"
          className="back-link"
        >
          ← Back to Dashboard
        </Link>


        <p className="section-label">
          BODY MEASUREMENT
        </p>


        <h1>
          Upload your body video
        </h1>


        <p>
          Upload a short video of yourself so SmartFit can
          estimate your body measurements and prepare your
          virtual fitting profile.
        </p>

      </section>


      {/* =====================================================
          UPLOAD CONTENT
          ===================================================== */}

      <section className="upload-content">

        {/*
          Height calibrates normalized pose landmarks to centimetres. It is
          collected alongside the video rather than inferred from one
          uncalibrated camera recording.
        */}
        <div className="form-group upload-height-field">
          <label htmlFor="user-height-cm">
            Your height (cm)
          </label>

          <input
            id="user-height-cm"
            type="number"
            min="100"
            max="250"
            step="0.1"
            value={userHeightCm}
            onChange={(event) => setUserHeightCm(event.target.value)}
            placeholder="e.g. 175"
            required
            disabled={uploading}
          />
        </div>

        {!selectedFile ? (

          /* =================================================
             FILE DROP AREA
             ================================================= */

          <div
            className="upload-dropzone"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >

            <div className="upload-icon">
              🎥
            </div>


            <h2>
              Upload your video
            </h2>


              <p>
                Drag and drop your video here or choose a file
                from your computer.
              </p>


              <button
              type="button"
              className="primary-button"
              onClick={openFilePicker}
            >
              Choose Video
            </button>


            <input
              ref={fileInputRef}
              type="file"
              accept="video/mp4,video/webm,video/quicktime"
              onChange={handleInputChange}
              hidden
            />


            <p className="upload-hint">
              MP4, WebM, or MOV · Maximum 500 MB
            </p>

          </div>

        ) : (

          /* =================================================
             VIDEO PREVIEW
             ================================================= */

          <div className="video-preview-card">

            <div className="video-preview">

              <video
                src={previewUrl}
                controls
              />

            </div>


            <div className="video-information">

              <div>

                <p className="section-label">
                  SELECTED VIDEO
                </p>


                <h2>
                  {selectedFile.name}
                </h2>


                <p>
                  {formatFileSize(selectedFile.size)}
                </p>

              </div>


              <button
                type="button"
                className="secondary-button"
                onClick={removeVideo}
                disabled={uploading}
              >
                Remove
              </button>

            </div>


            {/* =================================================
                UPLOAD PROGRESS
                ================================================= */}

            {uploading && (
              <div className="upload-progress">

                <div className="upload-progress-header">

                  <span>
                    Uploading video...
                  </span>


                  <strong>
                    {uploadProgress}%
                  </strong>

                </div>


                <div className="progress-track">

                  <div
                    className="progress-bar"
                    style={{
                      width: `${uploadProgress}%`,
                    }}
                  />

                </div>

              </div>
            )}


            {/* =================================================
                SUCCESS MESSAGE
                ================================================= */}

            {success && (
              <div
                className="form-message success-message"
                role="status"
              >
                {success}
              </div>
            )}


            {/* =================================================
                BACKEND RESPONSE
                ================================================= */}

            {uploadedVideo && (
              <div className="video-upload-result">

                <p>
                  <strong>
                    Video ID:
                  </strong>{" "}
                  {uploadedVideo.video_id}
                </p>


                <p>
                  <strong>
                    Processing status:
                  </strong>{" "}
                  {uploadedVideo.processing_status}
                </p>


                {uploadedVideo.processing_error && (
                  <p>
                    <strong>
                      Processing note:
                    </strong>{" "}
                    {uploadedVideo.processing_error}
                  </p>
                )}

              </div>
            )}


            {/* =================================================
                UPLOAD BUTTON
                ================================================= */}

            <button
              type="button"
              className="primary-button upload-submit"
              onClick={handleUpload}
              disabled={uploading}
            >
              {uploading
                ? "Uploading..."
                : "Upload Video"}
            </button>

          </div>

        )}


        {/* =====================================================
            ERROR MESSAGE
            ===================================================== */}

        {error && (
          <div
            className="form-message error-message upload-error"
            role="alert"
          >
            {error}
          </div>
        )}

      </section>


      {/* =====================================================
          VIDEO GUIDELINES
          ===================================================== */}

      <section className="upload-guidelines">

        <div className="upload-guidelines-header">

          <p className="section-label">
            VIDEO GUIDELINES
          </p>


          <h2>
            How to record your video
          </h2>


          <p>
            A clear and consistent video helps SmartFit produce
            more accurate body measurements.
          </p>

        </div>


        <div className="guidelines-grid">

          {/* Guideline 1 */}

          <div className="guideline-card">

            <span className="guideline-number">
              01
            </span>


            <h3>
              Stand upright
            </h3>


            <p>
              Stand straight with your arms slightly away from
              your body so your body outline remains visible.
            </p>

          </div>


          {/* Guideline 2 */}

          <div className="guideline-card">

            <span className="guideline-number">
              02
            </span>


            <h3>
              Use good lighting
            </h3>


            <p>
              Record in a well-lit environment where your body
              can be clearly distinguished from the background.
            </p>

          </div>


          {/* Guideline 3 */}

          <div className="guideline-card">

            <span className="guideline-number">
              03
            </span>


            <h3>
              Keep your full body visible
            </h3>


            <p>
              Make sure your entire body remains inside the
              camera frame throughout the recording.
            </p>

          </div>


          {/* Guideline 4 */}

          <div className="guideline-card">

            <span className="guideline-number">
              04
            </span>


            <h3>
              Move slowly
            </h3>


            <p>
              Rotate slowly and steadily so the system can
              capture enough information for processing.
            </p>

          </div>

        </div>

      </section>

    </main>
  );
}


export default UploadVideo;
