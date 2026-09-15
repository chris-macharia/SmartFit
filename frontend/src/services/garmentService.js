/**
 * SmartFit Garment API Service
 *
 * This module contains frontend functions for communicating
 * with the SmartFit garment-related backend endpoints.
 *
 * Retailer operations:
 * - Create a garment
 * - Retrieve own garments
 * - Retrieve a specific garment
 * - Update a garment
 * - Delete a garment
 *
 * Customer operation:
 * - Retrieve garments available for virtual fitting
 */

import { apiRequest } from "./api";


/**
 * Create a new garment.
 *
 * This operation is restricted to retailer accounts
 * by the backend.
 *
 * @param {Object} garmentData - Garment measurement data.
 * @returns {Promise<Object>} Created garment.
 */
export async function createGarment(garmentData) {
    return apiRequest("/api/garments/", {
        method: "POST",
        body: JSON.stringify(garmentData),
    });
}


/**
 * Retrieve garments belonging to the authenticated retailer.
 *
 * @returns {Promise<Response>} API response.
 */
export async function getMyGarments() {
    return apiRequest("/api/garments/", {
        method: "GET",
    });
}


/**
 * Retrieve all garments available for customer virtual fitting.
 *
 * Unlike getMyGarments(), this endpoint returns garments
 * registered by retailers and is intended for customers
 * selecting a garment for virtual fitting.
 *
 * @returns {Promise<Response>} API response.
 */
export async function getAvailableGarments() {
    return apiRequest("/api/garments/available", {
        method: "GET",
    });
}


/**
 * Retrieve a specific garment by ID.
 *
 * @param {string} garmentId - Garment UUID.
 * @returns {Promise<Response>} API response.
 */
export async function getGarment(garmentId) {
    return apiRequest(`/api/garments/${garmentId}`, {
        method: "GET",
    });
}


/**
 * Update an existing garment.
 *
 * This operation is restricted to the retailer
 * who owns the garment.
 *
 * @param {string} garmentId - Garment UUID.
 * @param {Object} garmentData - Updated garment measurements.
 * @returns {Promise<Response>} API response.
 */
export async function updateGarment(
    garmentId,
    garmentData
) {
    return apiRequest(`/api/garments/${garmentId}`, {
        method: "PUT",
        body: JSON.stringify(garmentData),
    });
}


/**
 * Delete an existing garment.
 *
 * This operation is restricted to the retailer
 * who owns the garment.
 *
 * @param {string} garmentId - Garment UUID.
 * @returns {Promise<Response>} API response.
 */
export async function deleteGarment(garmentId) {
    return apiRequest(
        `/api/garments/${garmentId}`,
        {
            method: "DELETE",
        }
    );
}