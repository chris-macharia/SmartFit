/**
 * SmartFit Authentication Service
 *
 * This module contains all frontend functions that communicate
 * with the authentication-related backend endpoints.
 *
 * The React pages should call these functions instead of making
 * fetch() requests directly. This keeps our UI code focused on
 * presentation and user interaction.
 */

import { apiRequest } from "./api";


/**
 * Register a new SmartFit user.
 *
 * Backend:
 * POST /api/users/
 *
 * @param {object} userData - Registration information
 * @returns {Promise<Response>} Backend HTTP response
 */
export async function registerUser(userData) {
    return apiRequest("/api/users/", {
        method: "POST",

        // Convert the JavaScript object into JSON because
        // FastAPI expects a JSON request body.
        body: JSON.stringify(userData),
    });
}


/**
 * Authenticate an existing SmartFit user.
 *
 * Backend:
 * POST /api/users/login
 *
 * @param {object} credentials - User email and password
 * @returns {Promise<Response>} Backend HTTP response
 */
export async function loginUser(credentials) {
    return apiRequest("/api/users/login", {
        method: "POST",
        body: JSON.stringify(credentials),
    });
}


/**
 * Retrieve the currently authenticated user.
 *
 * Backend:
 * GET /api/users/me
 *
 * @param {string} token - JWT access token
 * @returns {Promise<Response>} Backend HTTP response
 */
export async function getCurrentUser(token) {
    return apiRequest("/api/users/me", {
        method: "GET",

        // The JWT is sent using the standard Bearer authentication
        // scheme expected by FastAPI.
        headers: {
            Authorization: `Bearer ${token}`,
        },
    });
}