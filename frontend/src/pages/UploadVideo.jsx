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
 * 9. Remember the completed video ID for the avatar-generation page.
 * 10. Allow the user to delete the uploaded video.
 */

import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  Link,
} from "react-router-dom";

import {
  uploadVideo,
  getVideo,
  deleteVideo,
} from "../services/videoService";


function UploadVideo() {

  // ============================================================
  // FILE INPUT REFERENCE
  // ============================================================

  const fileInputRef = useRef(null);


  // ============================================================
  // PROCESSING SECTION REFERENCE
  // ============================================================

  const processingSectionRef = useRef(null);


  // ============================================================
  // COMPONENT STATE
  // ============================================================

  const [selectedFile, setSelectedFile] = useState(null);

  const [userHeightCm, setUserHeightCm] = useState("");

  const [previewUrl, setPreviewUrl] = useState("");

  const [error, setError] = useState("");

  const [uploading, setUploading] = useState(false);

  const [uploadProgress, setUploadProgress] = useState(0);

  const [success, setSuccess] = useState("");

  const [uploadedVideo, setUploadedVideo] = useState(null);

  const [processing, setProcessing] = useState(false);

  const [deleting, setDeleting] = useState(false);


  // ============================================================
  // FILE CONFIGURATION
  // ============================================================

  /**
   * Maximum accepted video size.
   *
   * 500 MB.
   */
  const MAX_FILE_SIZE =
    500 * 1024 * 1024;


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

  function handleFileSelect(file) {

    setError("");
    setSuccess("");
    setUploadedVideo(null);
    setProcessing(false);
    setUploadProgress(0);


    if (!file) {
      return;
    }


    // ----------------------------------------------------------
    // Validate file type.
    // ----------------------------------------------------------

    if (
      !ACCEPTED_VIDEO_TYPES.includes(
        file.type
      )
    ) {

      setError(
        "Please select an MP4, WebM, or MOV video file."
      );

      return;
    }


    // ----------------------------------------------------------
    // Validate file size.
    // ----------------------------------------------------------

    if (file.size > MAX_FILE_SIZE) {

      setError(
        "The selected video is too large. Please choose a video smaller than 500 MB."
      );

      return;
    }


    // ----------------------------------------------------------
    // Release previous preview URL.
    // ----------------------------------------------------------

    if (previewUrl) {
      URL.revokeObjectURL(
        previewUrl
      );
    }


    // ----------------------------------------------------------
    // Create new preview URL.
    // ----------------------------------------------------------

    const videoUrl =
      URL.createObjectURL(file);


    setSelectedFile(file);

    setPreviewUrl(videoUrl);
  }


  // ============================================================
  // FILE INPUT HANDLER
  // ============================================================

  function handleInputChange(event) {

    const file =
      event.target.files[0];

    handleFileSelect(file);
  }


  // ============================================================
  // OPEN FILE PICKER
  // ============================================================

  function openFilePicker() {

    fileInputRef.current?.click();
  }


  // ============================================================
  // DRAG AND DROP
  // ============================================================

  function handleDrop(event) {

    event.preventDefault();

    const file =
      event.dataTransfer.files[0];

    handleFileSelect(file);
  }


  function handleDragOver(event) {

    event.preventDefault();
  }


  // ============================================================
  // REMOVE LOCAL VIDEO
  // ============================================================

  function removeVideo() {

    if (previewUrl) {

      URL.revokeObjectURL(
        previewUrl
      );
    }


    setSelectedFile(null);

    setPreviewUrl("");

    setError("");

    setSuccess("");

    setUploadProgress(0);


    if (fileInputRef.current) {

      fileInputRef.current.value = "";
    }
  }


  // ============================================================
  // UPLOAD VIDEO
  // ============================================================

  async function handleUpload() {

    if (!selectedFile) {

      setError(
        "Please select a video before continuing."
      );

      return;
    }


    const parsedHeight =
      Number(userHeightCm);


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


    setError("");

    setSuccess("");

    setUploadedVideo(null);

    setProcessing(false);

    setUploading(true);

    setUploadProgress(0);


    try {

      // --------------------------------------------------------
      // Upload video.
      // --------------------------------------------------------

      const video =
        await uploadVideo(
          selectedFile,
          parsedHeight
        );


      // --------------------------------------------------------
      // Store backend response.
      // --------------------------------------------------------

      setUploadedVideo(video);

      setUploadProgress(100);

      setProcessing(true);


      setSuccess(
        "Video uploaded successfully."
      );


      // --------------------------------------------------------
      // Remember the video ID.
      // --------------------------------------------------------

      localStorage.setItem(
        "smartfit_latest_video_id",
        video.video_id
      );


      // --------------------------------------------------------
      // Release local preview.
      // --------------------------------------------------------

      if (previewUrl) {

        URL.revokeObjectURL(
          previewUrl
        );
      }


      setSelectedFile(null);

      setPreviewUrl("");


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

    if (!uploadedVideo?.video_id) {
      return;
    }


    if (
      uploadedVideo.processing_status ===
        "completed" ||
      uploadedVideo.processing_status ===
        "failed"
    ) {

      setProcessing(false);

      return;
    }


    setProcessing(true);


    const pollInterval =
      setInterval(
        async () => {

          try {

            const latestVideo =
              await getVideo(
                uploadedVideo.video_id
              );


            setUploadedVideo(
              latestVideo
            );


            // --------------------------------------------------
            // Keep the video ID persisted.
            // --------------------------------------------------

            localStorage.setItem(
              "smartfit_latest_video_id",
              latestVideo.video_id
            );


            if (
              latestVideo.processing_status ===
                "completed" ||
              latestVideo.processing_status ===
                "failed"
            ) {

              clearInterval(
                pollInterval
              );

              setProcessing(false);
            }

          } catch (err) {

            clearInterval(
              pollInterval
            );

            setProcessing(false);

            setError(
              err.message ||
              "Unable to check the video processing status."
            );
          }

        },
        2000
      );


    return () => {

      clearInterval(
        pollInterval
      );
    };

  }, [
    uploadedVideo?.video_id,
    uploadedVideo?.processing_status,
  ]);


  // ============================================================
  // SCROLL TO PROCESSING SECTION
  // ============================================================

  useEffect(() => {

    if (!uploadedVideo?.video_id) {
      return;
    }


    const timeoutId =
      setTimeout(() => {

        processingSectionRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "center",
        });

      }, 100);


    return () => {

      clearTimeout(
        timeoutId
      );
    };

  }, [
    uploadedVideo?.video_id,
  ]);


  // ============================================================
  // DELETE UPLOADED VIDEO
  // ============================================================

  async function handleDeleteVideo() {

    if (!uploadedVideo?.video_id) {
      return;
    }


    const confirmed =
      window.confirm(
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


      // --------------------------------------------------------
      // Remove the remembered video ID.
      // --------------------------------------------------------

      localStorage.removeItem(
        "smartfit_latest_video_id"
      );


      setUploadedVideo(null);

      setProcessing(false);

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

  function formatFileSize(bytes) {

    if (
      bytes <
      1024 * 1024
    ) {

      return `${(
        bytes / 1024
      ).toFixed(1)} KB`;
    }


    return `${(
      bytes /
      (1024 * 1024)
    ).toFixed(2)} MB`;
  }


  // ============================================================
  // PROCESSING STATUS HELPERS
  // ============================================================

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


  const processingFailed =
    uploadedVideo?.processing_status ===
    "failed";


  const processingCompleted =
    uploadedVideo?.processing_status ===
    "completed";


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
              setUserHeightCm(
                event.target.value
              )
            }
            placeholder="e.g. 175"
            required
            disabled={uploading}
          />

        </div>


        {/* ====================================================
            FILE SELECTION
            ==================================================== */}

        {!selectedFile &&
        !uploadedVideo ? (

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


              <div className="processing-step-line">

                <div
                  className={
                    `processing-step-line-progress ${
                      uploadedVideo.processing_status ===
                      "processing"
                        ? ""
                        : "completed"
                    }`
                  }
                />

              </div>


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


              {/* ==================================================
                  PROCESSING ANIMATION
                  ================================================== */}

              {processing &&
              !processingFailed &&
              !processingCompleted && (

                <div className="processing-animation">

                  <div className="processing-progress-track">

                    <div className="processing-progress-bar" />

                  </div>


                  <span>
                    Processing your video...
                  </span>

                </div>
              )}


              {/* ==================================================
                  MEASUREMENTS
                  ================================================== */}

              {processingCompleted &&
              uploadedVideo.measurement && (

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

                    {/* Height */}

                    <div className="measurement-item">

                      <span>
                        Height
                      </span>


                      <strong>
                        {uploadedVideo.measurement.height?.toFixed(
                          2
                        )} cm
                      </strong>

                    </div>


                    {/* Chest */}

                    <div className="measurement-item">

                      <span>
                        Chest
                      </span>


                      <strong>
                        {uploadedVideo.measurement.chest !==
                        null
                          ? `${uploadedVideo.measurement.chest.toFixed(
                              2
                            )} cm`
                          : "Not available"}
                      </strong>

                    </div>


                    {/* Waist */}

                    <div className="measurement-item">

                      <span>
                        Waist
                      </span>


                      <strong>
                        {uploadedVideo.measurement.waist !==
                        null
                          ? `${uploadedVideo.measurement.waist.toFixed(
                              2
                            )} cm`
                          : "Not available"}
                      </strong>

                    </div>


                    {/* Hips */}

                    <div className="measurement-item">

                      <span>
                        Hips
                      </span>


                      <strong>
                        {uploadedVideo.measurement.hips !==
                        null
                          ? `${uploadedVideo.measurement.hips.toFixed(
                              2
                            )} cm`
                          : "Not available"}
                      </strong>

                    </div>


                    {/* Shoulder Width */}

                    <div className="measurement-item">

                      <span>
                        Shoulder Width
                      </span>


                      <strong>
                        {uploadedVideo.measurement.shoulder_width.toFixed(
                          2
                        )} cm
                      </strong>

                    </div>


                    {/* Inseam */}

                    <div className="measurement-item">

                      <span>
                        Inseam
                      </span>


                      <strong>
                        {uploadedVideo.measurement.inseam.toFixed(
                          2
                        )} cm
                      </strong>

                    </div>


                    {/* Confidence */}

                    <div className="measurement-item">

                      <span>
                        Confidence
                      </span>


                      <strong>
                        {(
                          uploadedVideo.measurement.confidence_score *
                          100
                        ).toFixed(1)}%
                      </strong>

                    </div>

                  </div>


                  {/* ==================================================
                      GENERATE AVATAR BUTTON
                      ================================================== */}

                  <div className="avatar-generation-action">

                    <Link
                      to="/generate-avatar"
                      state={{
                        videoId:
                          uploadedVideo.video_id,
                      }}
                      className="primary-button generate-avatar-button"
                      style={{
                        marginTop: "24px",
                      }}
                    >
                      Generate Avatar →
                    </Link>

                  </div>

                </div>
              )}


              {/* ==================================================
                  PROCESSING ERROR
                  ================================================== */}

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

      {!uploadedVideo && (

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

      )}

    </main>
  );
}


export default UploadVideo;