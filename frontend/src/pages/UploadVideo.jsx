/**
 * SmartFit Upload Video Page
 *
 * This page provides the interface for uploading a user's
 * body video for the SmartFit virtual fitting process.
 *
 * Frontend responsibilities:
 *
 * 1. Allow the user to select a video file.
 * 2. Validate the selected file.
 * 3. Display a video preview.
 * 4. Collect the user's height.
 * 5. Upload the video to the SmartFit backend.
 * 6. Poll the backend for processing status.
 * 7. Display processing progress.
 * 8. Display body measurements when processing completes.
 * 9. Allow the user to delete the uploaded video.
 */

import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";

import {
  uploadVideo,
  getVideo,
  deleteVideo,
} from "../services/videoService";


function UploadVideo() {

  // ============================================================
  // FILE INPUT REFERENCE
  // ============================================================

  // Reference to the hidden file input.
  const fileInputRef = useRef(null);


  // ============================================================
  // PROCESSING SECTION REFERENCE
  // ============================================================

  /*
   * Reference to the processing status section.
   *
   * After a successful upload, the page automatically
   * scrolls this section into view so the user can see
   * what SmartFit is currently doing.
   */
  const processingSectionRef = useRef(null);


  // ============================================================
  // COMPONENT STATE
  // ============================================================

  // Store the selected local video file.
  const [selectedFile, setSelectedFile] = useState(null);


  // Store the user's declared height.
  const [userHeightCm, setUserHeightCm] = useState("");


  // Store the temporary browser URL used for video preview.
  const [previewUrl, setPreviewUrl] = useState("");


  // Store validation or API errors.
  const [error, setError] = useState("");


  // Track whether the upload request is currently running.
  const [uploading, setUploading] = useState(false);


  // Upload progress.
  //
  // Fetch does not provide upload progress events.
  // Therefore this represents the upload request state.
  const [uploadProgress, setUploadProgress] = useState(0);


  // Store a successful upload message.
  const [success, setSuccess] = useState("");


  /*
   * Store the video returned by the backend.
   *
   * This object is also updated during polling so the UI
   * always reflects the latest backend processing state.
   */
  const [uploadedVideo, setUploadedVideo] = useState(null);


  // Track whether processing is currently being polled.
  const [processing, setProcessing] = useState(false);


  // Track whether the delete request is running.
  const [deleting, setDeleting] = useState(false);


  // ============================================================
  // FILE CONFIGURATION
  // ============================================================

  /**
   * Maximum accepted video size.
   *
   * 500 MB.
   */
  const MAX_FILE_SIZE = 500 * 1024 * 1024;


  /**
   * Accepted video MIME types.
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
    setProcessing(false);
    setUploadProgress(0);


    // Make sure a file exists.
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
        "The selected video is too large. Please choose a video smaller than 500 MB."
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


    // Store selected file and preview.
    setSelectedFile(file);
    setPreviewUrl(videoUrl);
  }


  // ============================================================
  // FILE INPUT HANDLER
  // ============================================================

  /**
   * Handle selection through the file picker.
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
  // REMOVE LOCAL VIDEO
  // ============================================================

  /**
   * Remove the currently selected local video.
   *
   * This does NOT delete an already-uploaded backend video.
   */
  function removeVideo() {

    // Release temporary browser URL.
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }


    // Reset local upload state.
    setSelectedFile(null);
    setPreviewUrl("");
    setError("");
    setSuccess("");
    setUploadProgress(0);


    // Reset file input.
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }


  // ============================================================
  // UPLOAD VIDEO
  // ============================================================

  /**
   * Upload the selected video to the SmartFit backend.
   */
  async function handleUpload() {

    // Make sure a file was selected.
    if (!selectedFile) {

      setError(
        "Please select a video before continuing."
      );

      return;
    }


    // ----------------------------------------------------------
    // Validate height
    // ----------------------------------------------------------

    const parsedHeight = Number(userHeightCm);


    if (
      !Number.isFinite(parsedHeight) ||
      parsedHeight < 100 ||
      parsedHeight > 250
    ) {

      setError(
        "Please enter your height between 100 cm and 250 cm."
      );

      return;
    }


    // ----------------------------------------------------------
    // Clear previous feedback
    // ----------------------------------------------------------

    setError("");
    setSuccess("");
    setUploadedVideo(null);
    setProcessing(false);


    // ----------------------------------------------------------
    // Begin upload
    // ----------------------------------------------------------

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


      // Upload request completed.
      setUploadProgress(100);


      // Begin processing state.
      setProcessing(true);


      // Display success message.
      setSuccess(
        "Video uploaded successfully."
      );


      // --------------------------------------------------------
      // Release local preview
      // --------------------------------------------------------

      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }


      // --------------------------------------------------------
      // Clear selected local file
      // --------------------------------------------------------

      setSelectedFile(null);
      setPreviewUrl("");


      // Reset file input.
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }

    } catch (err) {

      setError(
        err.message ||
        "An error occurred while uploading the video."
      );

    } finally {

      setUploading(false);
    }
  }


  // ============================================================
  // POLL VIDEO PROCESSING STATUS
  // ============================================================

  useEffect(() => {

    /*
     * Do not poll if there is no uploaded video.
     */
    if (!uploadedVideo?.video_id) {
      return;
    }


    /*
     * If the backend already says completed or failed,
     * there is nothing left to poll.
     */
    if (
      uploadedVideo.processing_status === "completed" ||
      uploadedVideo.processing_status === "failed"
    ) {

      setProcessing(false);

      return;
    }


    /*
     * Start polling the backend.
     *
     * The frontend does not perform any computer vision.
     * It simply asks the backend for the latest state.
     */
    setProcessing(true);


    const pollInterval = setInterval(async () => {

      try {

        const latestVideo = await getVideo(
          uploadedVideo.video_id
        );


        // Update the UI with the latest backend state.
        setUploadedVideo(latestVideo);


        /*
         * Stop polling when processing finishes.
         */
        if (
          latestVideo.processing_status === "completed" ||
          latestVideo.processing_status === "failed"
        ) {

          clearInterval(pollInterval);

          setProcessing(false);
        }

      } catch (err) {

        /*
         * Stop polling if the status request itself fails.
         */
        clearInterval(pollInterval);

        setProcessing(false);

        setError(
          err.message ||
          "Unable to check the video processing status."
        );
      }

    }, 2000);


    /*
     * Clean up the polling interval when the component
     * unmounts or the video changes.
     */
    return () => {
      clearInterval(pollInterval);
    };

  }, [
    uploadedVideo?.video_id,
    uploadedVideo?.processing_status,
  ]);


  // ============================================================
  // SCROLL TO ACTIVE PROCESSING SECTION
  // ============================================================

  useEffect(() => {

    /*
     * Only scroll after a video has successfully been
     * uploaded and a video ID exists.
     */
    if (!uploadedVideo?.video_id) {
      return;
    }


    /*
     * Give React time to render the processing section
     * before scrolling to it.
     */
    const timeoutId = setTimeout(() => {

      processingSectionRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });

    }, 100);


    /*
     * Clean up the timeout if necessary.
     */
    return () => {
      clearTimeout(timeoutId);
    };

  }, [uploadedVideo?.video_id]);


  // ============================================================
  // DELETE UPLOADED VIDEO
  // ============================================================

  /**
   * Delete the uploaded video from the backend.
   */
  async function handleDeleteVideo() {

    if (!uploadedVideo?.video_id) {
      return;
    }


    const confirmed = window.confirm(
      "Are you sure you want to delete this video?"
    );


    if (!confirmed) {
      return;
    }


    setDeleting(true);
    setError("");


    try {

      await deleteVideo(
        uploadedVideo.video_id
      );


      // Reset backend video state.
      setUploadedVideo(null);


      // Stop processing state.
      setProcessing(false);


      // Clear success message.
      setSuccess(
        "Video deleted successfully."
      );

    } catch (err) {

      setError(
        err.message ||
        "Failed to delete the video."
      );

    } finally {

      setDeleting(false);
    }
  }


  // ============================================================
  // FORMAT FILE SIZE
  // ============================================================

  /**
   * Format bytes into a readable file size.
   *
   * @param {number} bytes - File size in bytes.
   * @returns {string} Formatted file size.
   */
  function formatFileSize(bytes) {

    if (bytes < 1024 * 1024) {

      return `${(bytes / 1024).toFixed(1)} KB`;
    }


    return `${(
      bytes /
      (1024 * 1024)
    ).toFixed(2)} MB`;
  }


  // ============================================================
  // PROCESSING STATUS HELPERS
  // ============================================================

  /**
   * Convert the backend status into a user-friendly label.
   */
  function getStatusLabel(status) {

    switch (status) {

      case "uploaded":
        return "Uploaded";

      case "processing":
        return "Processing";

      case "completed":
        return "Processing completed";

      case "failed":
        return "Processing failed";

      default:
        return status || "Waiting";
    }
  }


  /**
   * Determine whether processing has failed.
   */
  const processingFailed =
    uploadedVideo?.processing_status === "failed";


  /**
   * Determine whether processing has completed.
   */
  const processingCompleted =
    uploadedVideo?.processing_status === "completed";


  // ============================================================
  // RENDER
  // ============================================================

  return (

    <main className="upload-page">

      {/* ======================================================
          PAGE HEADER
          ====================================================== */}

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


      {/* ======================================================
          UPLOAD CONTENT
          ====================================================== */}

      <section className="upload-content">

        {/* ====================================================
            HEIGHT
            ==================================================== */}

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
            onChange={(event) =>
              setUserHeightCm(event.target.value)
            }
            placeholder="e.g. 175"
            required
            disabled={uploading}
          />

        </div>


        {/* ====================================================
            FILE SELECTION
            ==================================================== */}

        {!selectedFile && !uploadedVideo ? (

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

        ) : selectedFile ? (

          /* ==================================================
             VIDEO PREVIEW
             ================================================== */

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
                  {formatFileSize(
                    selectedFile.size
                  )}
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


            {/* ==================================================
                UPLOAD PROGRESS
                ================================================== */}

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


            {/* ==================================================
                UPLOAD BUTTON
                ================================================== */}

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

        ) : null}


        {/* ====================================================
            PROCESSING STATUS
            ==================================================== */}

        {uploadedVideo && (

          <section
            ref={processingSectionRef}
            className="processing-status-card"
          >

            <div className="processing-status-header">

              <p className="section-label">
                VIDEO PROCESSING
              </p>


              <h2>
                {processingFailed
                  ? "Processing failed"
                  : processingCompleted
                    ? "Your measurements are ready"
                    : "Analyzing your video"}
              </h2>


              <p>
                {processingFailed
                  ? "SmartFit could not finish processing this video."
                  : processingCompleted
                    ? "SmartFit has successfully processed your video."
                    : "SmartFit is analyzing your video to estimate your body measurements."}
              </p>

            </div>


            {/* ==================================================
                PROCESSING TIMELINE
                ================================================== */}

            <div className="processing-timeline">

              {/* ------------------------------------------------
                  UPLOADED
                  ------------------------------------------------ */}

              <div className="processing-step completed">

                <div className="processing-step-marker">
                  ✓
                </div>


                <div className="processing-step-content">

                  <strong>
                    Uploaded
                  </strong>


                  <span>
                    Video successfully received
                  </span>

                </div>

              </div>


              {/* ------------------------------------------------
                  CONNECTOR
                  ------------------------------------------------ */}

              <div className="processing-step-line">

                <div
                  className={
                    `processing-step-line-progress ${
                      uploadedVideo.processing_status === "processing"
                        ? ""
                        : "completed"
                    }`
                  }
                />

              </div>  


              {/* ------------------------------------------------
                  PROCESSING
                  ------------------------------------------------ */}

              <div
                className={
                  `processing-step ${
                    processingFailed
                      ? "failed"
                      : processingCompleted
                        ? "completed"
                        : "active"
                  }`
                }
              >

                <div className="processing-step-marker">

                  {processingFailed
                    ? "!"
                    : processingCompleted
                      ? "✓"
                      : "●"}

                </div>


                <div className="processing-step-content">

                  <strong>
                    {processingFailed
                      ? "Processing failed"
                      : processingCompleted
                        ? "Processed"
                        : "Processing"}
                  </strong>


                  <span>
                    {processingFailed
                      ? "SmartFit could not process this video"
                      : processingCompleted
                        ? "Body measurements generated"
                        : "Analyzing body movement and proportions"}
                  </span>

                </div>

              </div>


              {/* ------------------------------------------------
                  PROCESSING ANIMATION
                  ------------------------------------------------ */}

              {processing && !processingFailed && !processingCompleted && (

                <div className="processing-animation">

                  <div className="processing-progress-track">

                    <div className="processing-progress-bar" />

                  </div>


                  <span>
                    Processing your video...
                  </span>

                </div>

              )}


              {/* ------------------------------------------------
                  COMPLETED CONNECTOR
                  ------------------------------------------------ */}

              {processingCompleted && (

                <div className="processing-step-line completed-line">

                  <div className="processing-step-line-progress completed" />

                </div>

              )}


              {/* ------------------------------------------------
                  MEASUREMENTS
                  ------------------------------------------------ */}

              {processingCompleted && uploadedVideo.measurements && (

                <div className="measurements-result">

                  <div className="measurements-header">

                    <p className="section-label">
                      BODY MEASUREMENTS
                    </p>


                    <h3>
                      Your measurements
                    </h3>

                  </div>


                  <div className="measurement-grid">

                    {Object.entries(
                      uploadedVideo.measurements
                    ).map(([key, value]) => (

                      <div
                        className="measurement-item"
                        key={key}
                      >

                        <span>
                          {key
                            .replaceAll("_", " ")
                            .replace(
                              /\b\w/g,
                              (char) =>
                                char.toUpperCase()
                            )}
                        </span>


                        <strong>
                          {typeof value === "number"
                            ? `${value.toFixed(2)} cm`
                            : value}
                        </strong>

                      </div>

                    ))}

                  </div>

                </div>

              )}


              {/* ------------------------------------------------
                  PROCESSING ERROR
                  ------------------------------------------------ */}

              {processingFailed && (

                <div
                  className="form-message error-message processing-error"
                  role="alert"
                >

                  {uploadedVideo.processing_error ||
                    "SmartFit was unable to process this video. Please try uploading another video."}

                </div>

              )}

            </div>


            {/* ==================================================
                CURRENT STATUS
                ================================================== */}

            <div className="processing-current-status">

              <span>
                Current status
              </span>


              <strong>
                {getStatusLabel(
                  uploadedVideo.processing_status
                )}
              </strong>

            </div>


            {/* ==================================================
                DELETE VIDEO
                ================================================== */}

            <button
              type="button"
              className="secondary-button delete-video-button"
              onClick={handleDeleteVideo}
              disabled={deleting}
            >
              {deleting
                ? "Deleting..."
                : "Delete Video"}
            </button>

          </section>

        )}


        {/* ====================================================
            SUCCESS MESSAGE
            ==================================================== */}

        {success && !uploadedVideo && (

          <div
            className="form-message success-message upload-success"
            role="status"
          >
            {success}
          </div>

        )}


        {/* ====================================================
            ERROR MESSAGE
            ==================================================== */}

        {error && (

          <div
            className="form-message error-message upload-error"
            role="alert"
          >
            {error}
          </div>

        )}

      </section>


      {/* ======================================================
          VIDEO GUIDELINES
          ====================================================== */}

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