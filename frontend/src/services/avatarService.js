/**
 * SmartFit Avatar API Service
 *
 * Contains all API operations related to digital avatars.
 *
 * Responsibilities:
 *
 * 1. Generate an avatar from a completed body measurement.
 * 2. Retrieve an existing avatar.
 *
 * Authentication is handled automatically by apiRequest().
 */

import { apiRequest } from "./api";


// ============================================================
// GENERATE AVATAR
// ============================================================

/**
 * Generate a digital avatar from a body measurement.
 *
 * The backend endpoint expects the measurement UUID
 * as a query parameter.
 *
 *     POST /api/avatars/?measurement_id=<UUID>
 *
 * @param {string} measurementId - UUID of the body measurement.
 * @returns {Promise<Object>} Generated avatar information.
 */
export async function generateAvatar(measurementId) {

    const response = await apiRequest(
        `/api/avatars/?measurement_id=${encodeURIComponent(
            measurementId
        )}`,
        {
            method: "POST",
        }
    );


    // --------------------------------------------------------
    // Handle API errors.
    // --------------------------------------------------------

    if (!response.ok) {

        let message =
            "Failed to generate avatar.";

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
// GET AVATAR
// ============================================================

/**
 * Retrieve an existing avatar.
 *
 * @param {string} avatarId - UUID of the avatar.
 * @returns {Promise<Object>} Avatar information.
 */
export async function getAvatar(avatarId) {

    const response = await apiRequest(
        `/api/avatars/${avatarId}`,
        {
            method: "GET",
        }
    );


    // --------------------------------------------------------
    // Handle API errors.
    // --------------------------------------------------------

    if (!response.ok) {

        let message =
            "Failed to retrieve avatar.";

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