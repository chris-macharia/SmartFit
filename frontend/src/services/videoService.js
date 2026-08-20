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
 * @param {number} userHeightCm - User's declared height in centimetres
 * @returns {Promise<Object>} Uploaded video information
 */
export async function uploadVideo(file, userHeightCm) {

    const formData = new FormData();

    formData.append(
        "file",
        file
    );

    formData.append(
        "user_height_cm",
        String(userHeightCm)
    );

    const response = await apiRequest(
        "/api/videos/",
        {
            method: "POST",
            body: formData,
        }
    );


    if (!response.ok) {

        let message =
            "Failed to upload video.";

        try {

            const errorData =
                await response.json();

            if (errorData.detail) {
                message = errorData.detail;
            }

        } catch {
            // Keep the default error message.
        }

        throw new Error(message);
    }


    return response.json();
}


// ============================================================
// GET VIDEO
// ============================================================

/**
 * Get a single video belonging to the authenticated user.
 *
 * This endpoint is used by the frontend to monitor the
 * processing status after the upload has completed.
 *
 * @param {string} videoId - UUID of the video
 * @returns {Promise<Object>} Current video information
 */
export async function getVideo(videoId) {

    const response = await apiRequest(
        `/api/videos/${videoId}`,
        {
            method: "GET",
        }
    );


    if (!response.ok) {

        let message =
            "Failed to retrieve video.";

        try {

            const errorData =
                await response.json();

            if (errorData.detail) {
                message = errorData.detail;
            }

        } catch {
            // Keep the default error message.
        }

        throw new Error(message);
    }


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

    const response = await apiRequest(
        `/api/videos/${videoId}`,
        {
            method: "DELETE",
        }
    );


    if (!response.ok) {

        let message =
            "Failed to delete video.";

        try {

            const errorData =
                await response.json();

            if (errorData.detail) {
                message = errorData.detail;
            }

        } catch {
            // Keep the default error message.
        }

        throw new Error(message);
    }
}