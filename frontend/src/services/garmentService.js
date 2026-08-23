/**
 * SmartFit Garment API Service
 *
 * This module contains all frontend functions that communicate
 * with the SmartFit garment-related backend endpoints.
 *
 * Garments are currently managed by authenticated retailer
 * accounts.
 *
 * The service communicates with:
 *
 *     /api/garments/
 *
 * Authentication is handled automatically by apiRequest().
 */

import { apiRequest } from "./api";


// ============================================================
// CREATE GARMENT
// ============================================================

/**
 * Register a new garment for the authenticated retailer.
 *
 * Backend:
 * POST /api/garments/
 *
 * The backend obtains the retailer's user_id from the
 * authenticated JWT, so user_id must NOT be sent from
 * the frontend.
 *
 * @param {object} garmentData - Garment measurements.
 * @returns {Promise<Response>} Backend HTTP response.
 */
export async function createGarment(garmentData) {

    return apiRequest("/api/garments/", {
        method: "POST",

        /*
         * Convert the JavaScript object into JSON because
         * FastAPI expects a JSON request body.
         */
        body: JSON.stringify(garmentData),
    });
}


// ============================================================
// GET MY GARMENTS
// ============================================================

/**
 * Retrieve all garments belonging to the authenticated retailer.
 *
 * Backend:
 * GET /api/garments/
 *
 * @returns {Promise<Response>} Backend HTTP response.
 */
export async function getMyGarments() {

    return apiRequest("/api/garments/", {
        method: "GET",
    });
}


// ============================================================
// GET ONE GARMENT
// ============================================================

/**
 * Retrieve a specific garment belonging to the authenticated
 * retailer.
 *
 * Backend:
 * GET /api/garments/{garment_id}
 *
 * @param {string} garmentId - Garment UUID.
 * @returns {Promise<Response>} Backend HTTP response.
 */
export async function getGarment(garmentId) {

    return apiRequest(
        `/api/garments/${garmentId}`,
        {
            method: "GET",
        }
    );
}


// ============================================================
// UPDATE GARMENT
// ============================================================

/**
 * Update an existing garment.
 *
 * Backend:
 * PUT /api/garments/{garment_id}
 *
 * @param {string} garmentId - Garment UUID.
 * @param {object} garmentData - Updated measurements.
 * @returns {Promise<Response>} Backend HTTP response.
 */
export async function updateGarment(
    garmentId,
    garmentData
) {

    return apiRequest(
        `/api/garments/${garmentId}`,
        {
            method: "PUT",

            body: JSON.stringify(garmentData),
        }
    );
}


// ============================================================
// DELETE GARMENT
// ============================================================

/**
 * Delete an existing garment.
 *
 * Backend:
 * DELETE /api/garments/{garment_id}
 *
 * @param {string} garmentId - Garment UUID.
 * @returns {Promise<Response>} Backend HTTP response.
 */
export async function deleteGarment(garmentId) {

    return apiRequest(
        `/api/garments/${garmentId}`,
        {
            method: "DELETE",
        }
    );
}