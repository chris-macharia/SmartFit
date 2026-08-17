/**
 * SmartFit Video API Service
 *
 * Contains all API operations related to user videos.
 */

import { apiRequest } from "./api";


// ============================================================
// UPLOAD VIDEO
// ============================================================

/**
 * Upload a video for the authenticated user.
 *
 * @param {File} file - Video selected by the user
 * @returns {Promise<Object>} Uploaded video information
 */
export async function uploadVideo(file) {

    /*
     * Create a FormData object because the FastAPI
     * endpoint expects a multipart file upload.
     */
    const formData = new FormData();


    /*
     * The field name MUST match the FastAPI endpoint:
     *
     *     file: UploadFile = File(...)
     */
    formData.append(
        "file",
        file
    );


    /*
     * Send the video to the backend.
     *
     * apiRequest() automatically:
     *
     * 1. Retrieves the JWT from localStorage.
     * 2. Adds the Authorization header.
     * 3. Detects that this is FormData.
     * 4. Allows the browser to create the multipart
     *    Content-Type and boundary.
     */
    const response = await apiRequest(
        "/api/videos/",
        {
            method: "POST",
            body: formData,
        }
    );


    // ========================================================
    // HANDLE UPLOAD ERROR
    // ========================================================

    if (!response.ok) {

        let message =
            "Failed to upload video.";


        try {

            const errorData =
                await response.json();


            if (errorData.detail) {

                message =
                    errorData.detail;
            }

        } catch {

            /*
             * Keep the default error message if the
             * response is not valid JSON.
             */
        }


        throw new Error(message);
    }


    // ========================================================
    // RETURN BACKEND RESPONSE
    // ========================================================

    return response.json();
}


// ============================================================
// DELETE VIDEO
// ============================================================

/**
 * Delete a video belonging to the authenticated user.
 *
 * @param {string} videoId - UUID of the video
 */
export async function deleteVideo(videoId) {

    /*
     * apiRequest() automatically attaches the JWT.
     */
    const response = await apiRequest(
        `/api/videos/${videoId}`,
        {
            method: "DELETE",
        }
    );


    // ========================================================
    // HANDLE DELETE ERROR
    // ========================================================

    if (!response.ok) {

        let message =
            "Failed to delete video.";


        try {

            const errorData =
                await response.json();


            if (errorData.detail) {

                message =
                    errorData.detail;
            }

        } catch {

            /*
             * Keep the default error message.
             */
        }


        throw new Error(message);
    }
}