/**
 * SmartFit API Client
 *
 * Provides a reusable function for communicating
 * with the SmartFit FastAPI backend.
 *
 * Responsibilities:
 *
 * 1. Build the complete API URL.
 * 2. Automatically attach the stored JWT.
 * 3. Set appropriate request headers.
 * 4. Correctly handle JSON requests.
 * 5. Correctly handle FormData requests such as video uploads.
 */


// ============================================================
// API CONFIGURATION
// ============================================================

/*
 * Base URL of the SmartFit FastAPI backend.
 *
 * This value is loaded from the Vite environment configuration.
 *
 * Example:
 *
 * VITE_API_URL=http://127.0.0.1:8000
 */
const API_BASE_URL = import.meta.env.VITE_API_URL;


// ============================================================
// API REQUEST
// ============================================================

/**
 * Send a request to the SmartFit backend.
 *
 * Authentication:
 *
 * If a JWT exists in localStorage under "smartfit_token",
 * it is automatically sent using the standard Bearer
 * authentication scheme.
 *
 * This means individual services such as videoService.js
 * do not need to manually attach the JWT.
 *
 * JSON requests:
 *
 *     Content-Type: application/json
 *
 * FormData requests:
 *
 *     The browser automatically creates the correct
 *     multipart/form-data Content-Type and boundary.
 *
 * @param {string} endpoint - API endpoint.
 * @param {object} options - Fetch API options.
 * @returns {Promise<Response>} HTTP response.
 */
export async function apiRequest(endpoint, options = {}) {

    // ========================================================
    // BUILD REQUEST URL
    // ========================================================

    /*
     * Combine the configured API base URL with
     * the requested endpoint.
     */
    const url = `${API_BASE_URL}${endpoint}`;


    // ========================================================
    // RETRIEVE AUTHENTICATION TOKEN
    // ========================================================

    /*
     * Retrieve the JWT stored by AuthContext during login.
     *
     * AuthContext stores the token using:
     *
     *     localStorage.setItem(
     *         "smartfit_token",
     *         data.access_token
     *     );
     */
    const token = localStorage.getItem(
        "smartfit_token"
    );


    // ========================================================
    // PREPARE HEADERS
    // ========================================================

    /*
     * Start with any headers supplied by the individual
     * API service.
     */
    const headers = {
        ...options.headers,
    };


    // ========================================================
    // ATTACH JWT AUTHENTICATION
    // ========================================================

    /*
     * If a token exists, automatically attach it to
     * the request using the Bearer authentication scheme.
     *
     * FastAPI's authentication dependency expects:
     *
     *     Authorization: Bearer <JWT>
     */
    if (token) {

        headers["Authorization"] =
            `Bearer ${token}`;
    }


    // ========================================================
    // HANDLE CONTENT TYPE
    // ========================================================

    /*
     * FormData requests require special handling.
     *
     * When uploading a video, the request body is FormData.
     *
     * We must NOT manually set:
     *
     *     Content-Type: multipart/form-data
     *
     * because the browser needs to automatically add the
     * multipart boundary.
     */
    if (!(options.body instanceof FormData)) {

        /*
         * Normal requests use JSON.
         */
        headers["Content-Type"] =
            "application/json";

    } else {

        /*
         * If a service supplied a Content-Type header for
         * FormData, remove it.
         *
         * The browser will generate the correct value.
         */
        delete headers["Content-Type"];
    }


    // ========================================================
    // SEND REQUEST
    // ========================================================

    return fetch(url, {

        /*
         * Preserve the original request options.
         */
        ...options,

        /*
         * Use our prepared headers.
         */
        headers,
    });
}