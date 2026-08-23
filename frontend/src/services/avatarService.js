/**
 * SmartFit Avatar API Service
 *
 * Contains all API operations related to digital avatars.
 *
 * Responsibilities:
 *
 * 1. Generate an avatar from a completed body measurement.
 * 2. Retrieve an existing avatar.
 * 3. Retrieve the generated GLB avatar file.
 *
 * Authentication is handled automatically by apiRequest().
 */

import {
  apiRequest,
} from "./api";


// ============================================================
// GENERATE AVATAR
// ============================================================

/**
 * Generate a digital avatar from a body measurement.
 *
 * Backend endpoint:
 *
 *     POST /api/avatars/?measurement_id=<UUID>
 *
 * @param {string} measurementId - UUID of the body measurement.
 * @returns {Promise<Object>} Generated avatar information.
 */
export async function generateAvatar(
  measurementId
) {

  const response =
    await apiRequest(
      `/api/avatars/?measurement_id=${encodeURIComponent(
        measurementId
      )}`,
      {
        method: "POST",
      }
    );


  // ----------------------------------------------------------
  // Handle API errors.
  // ----------------------------------------------------------

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
 * Backend endpoint:
 *
 *     GET /api/avatars/{avatar_id}
 *
 * @param {string} avatarId - UUID of the avatar.
 * @returns {Promise<Object>} Avatar information.
 */
export async function getAvatar(
  avatarId
) {

  const response =
    await apiRequest(
      `/api/avatars/${encodeURIComponent(
        avatarId
      )}`,
      {
        method: "GET",
      }
    );


  // ----------------------------------------------------------
  // Handle API errors.
  // ----------------------------------------------------------

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


// ============================================================
// GET AVATAR FILE
// ============================================================

/**
 * Retrieve the generated GLB file for an avatar.
 *
 * Backend endpoint:
 *
 *     GET /api/avatars/{avatar_id}/file
 *
 * The authenticated API request retrieves the GLB file,
 * converts it into a Blob, and creates a temporary browser
 * Object URL.
 *
 * The returned Object URL can then be supplied to
 * React Three Fiber / Drei.
 *
 * @param {string} avatarId - UUID of the avatar.
 * @returns {Promise<string>} Browser Object URL for the GLB.
 */
export async function getAvatarFile(
  avatarId
) {

  const response =
    await apiRequest(
      `/api/avatars/${encodeURIComponent(
        avatarId
      )}/file`,
      {
        method: "GET",
      }
    );


  // ----------------------------------------------------------
  // Handle API errors.
  // ----------------------------------------------------------

  if (!response.ok) {

    let message =
      "Failed to retrieve avatar file.";

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


  // ----------------------------------------------------------
  // Convert GLB response into a Blob.
  // ----------------------------------------------------------

  const blob =
    await response.blob();


  // ----------------------------------------------------------
  // Create temporary browser Object URL.
  // ----------------------------------------------------------

  const objectUrl =
    URL.createObjectURL(blob);


  return objectUrl;
}