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
 * 6. Simulate the upload process.
 *
 * Backend integration will be added later.
 *
 * The eventual backend workflow will be:
 *
 *     Video Upload
 *          ↓
 *     FastAPI API
 *          ↓
 *     Computer Vision Processing
 *          ↓
 *     Body Measurements
 *          ↓
 *     Digital Avatar
 */

import { useRef, useState } from "react";
import { Link } from "react-router-dom";


function UploadVideo() {
  // Reference to the hidden file input.
  //
  // This allows the custom upload interface to trigger
  // the browser's native file selection dialog.
  const fileInputRef = useRef(null);


  // Store the selected video file.
  const [selectedFile, setSelectedFile] = useState(null);


  // Store the temporary browser URL used to preview the video.
  const [previewUrl, setPreviewUrl] = useState("");


  // Store validation errors.
  const [error, setError] = useState("");


  // Track whether the upload simulation is running.
  const [uploading, setUploading] = useState(false);


  // Store the simulated upload progress.
  const [uploadProgress, setUploadProgress] = useState(0);


  // Store a successful upload message.
  const [success, setSuccess] = useState("");


  /**
   * Maximum accepted video size.
   *
   * Five megabytes keeps the frontend test-friendly.
   *
   * The actual production limit will eventually be
   * determined by the backend upload configuration.
   */
  const MAX_FILE_SIZE = 5 * 1024 * 1024;


  /**
   * Accepted video formats.
   */
  const ACCEPTED_VIDEO_TYPES = [
    "video/mp4",
    "video/webm",
    "video/quicktime",
  ];


  /**
   * Validate and store a selected video file.
   */
  function handleFileSelect(file) {
    // Clear previous feedback.
    setError("");
    setSuccess("");
    setUploadProgress(0);


    // Make sure a file was actually selected.
    if (!file) {
      return;
    }


    // Check whether the selected file is a supported video type.
    if (!ACCEPTED_VIDEO_TYPES.includes(file.type)) {
      setError(
        "Please select an MP4, WebM, or MOV video file."
      );

      return;
    }


    // Check whether the file is within the allowed size.
    if (file.size > MAX_FILE_SIZE) {
      setError(
        "The selected video is too large. Please choose a video smaller than 5 MB."
      );

      return;
    }


    // Create a temporary browser URL for the video preview.
    const videoUrl = URL.createObjectURL(file);


    // Store the selected file and preview.
    setSelectedFile(file);
    setPreviewUrl(videoUrl);
  }


  /**
   * Handle selection through the standard file picker.
   */
  function handleInputChange(event) {
    const file = event.target.files[0];

    handleFileSelect(file);
  }


  /**
   * Open the browser's native file selection dialog.
   */
  function openFilePicker() {
    fileInputRef.current?.click();
  }


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


  /**
   * Remove the currently selected video.
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


    // Reset the file input so the same file can be
    // selected again if necessary.
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }


  /**
   * Simulate uploading the video.
   *
   * This function will eventually be replaced with a real
   * API request to the FastAPI backend.
   */
  function handleUpload() {
    if (!selectedFile) {
      setError("Please select a video before continuing.");

      return;
    }


    // Clear previous messages.
    setError("");
    setSuccess("");


    // Begin simulated upload.
    setUploading(true);
    setUploadProgress(0);


    let progress = 0;


    // Increase the progress value periodically.
    const interval = setInterval(() => {
      progress += 10;

      setUploadProgress(progress);


      // Complete the simulated upload at 100%.
      if (progress >= 100) {
        clearInterval(interval);

        setUploading(false);

        setSuccess(
          "Video uploaded successfully. Processing will begin shortly."
        );
      }
    }, 150);
  }


  /**
   * Format the file size into a readable value.
   */
  function formatFileSize(bytes) {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    }


    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  }


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
              MP4, WebM, or MOV · Maximum 5 MB
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
