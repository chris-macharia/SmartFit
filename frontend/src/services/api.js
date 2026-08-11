/**
 * SmartFit API Client
 *
 * This module provides a single reusable function for communicating
 * with the SmartFit FastAPI backend.
 *
 * Keeping the HTTP communication here means that components and
 * pages do not need to know the backend's base URL or manually
 * configure fetch requests.
 */

// Vite exposes variables prefixed with VITE_ to the frontend.
//
// Example:
// VITE_API_URL=http://127.0.0.1:8000
const API_BASE_URL = import.meta.env.VITE_API_URL;


/**
 * Send a request to the SmartFit backend.
 *
 * @param {string} endpoint - API path, e.g. "/api/users/"
 * @param {object} options - Standard Fetch API options
 * @returns {Promise<Response>} The raw HTTP response
 */
export async function apiRequest(endpoint, options = {}) {
    // Combine the configured backend URL with the requested endpoint.
    const url = `${API_BASE_URL}${endpoint}`;

    // Send the request using the browser's native Fetch API.
    return fetch(url, {
        ...options,

        // JSON is the standard format used by our FastAPI endpoints.
        // Individual requests can override these headers when necessary.
        headers: {
            "Content-Type": "application/json",
            ...options.headers,
        },
    });
}