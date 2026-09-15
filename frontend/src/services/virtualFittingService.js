/**
 * SmartFit Virtual Fitting API Service
 *
 * This module handles communication with the
 * SmartFit virtual-fitting backend.
 *
 * Virtual fitting combines:
 *
 *     Customer Avatar
 *            +
 *     Retailer Garment
 *            ↓
 *     Virtual Fitting Algorithm
 *            ↓
 *     Recommended Size
 *     Fit Result
 */

import { apiRequest } from "./api";


/**
 * Perform a virtual fitting.
 *
 * The authenticated customer's identity is determined
 * by the backend from the JWT token.
 *
 * The frontend only needs to provide:
 * - garment ID
 * - avatar ID
 *
 * @param {string} garmentId - Selected garment UUID.
 * @param {string} avatarId - Customer avatar UUID.
 * @returns {Promise<Object>} Virtual fitting result.
 */
export async function createVirtualFitting(
    garmentId,
    avatarId
) {
    const response = await apiRequest(
        "/api/virtual-fittings/",
        {
            method: "POST",
            body: JSON.stringify({
                garment_id: garmentId,
                avatar_id: avatarId,
            }),
        }
    );

    if (!response.ok) {
        let message =
            "Failed to perform virtual fitting.";

        try {
            const errorData =
                await response.json();

            if (errorData.detail) {
                if (
                    typeof errorData.detail ===
                    "string"
                ) {
                    message = errorData.detail;
                } else {
                    message =
                        "Unable to perform virtual fitting.";
                }
            }
        } catch {
            // Keep the default error message
            // if the response is not valid JSON.
        }

        throw new Error(message);
    }

    return response.json();
}


/**
 * Retrieve a previously created virtual fitting.
 *
 * @param {string} fittingId - Virtual fitting UUID.
 * @returns {Promise<Object>} Virtual fitting result.
 */
export async function getVirtualFitting(
    fittingId
) {
    const response = await apiRequest(
        `/api/virtual-fittings/${fittingId}`,
        {
            method: "GET",
        }
    );

    if (!response.ok) {
        let message =
            "Failed to retrieve virtual fitting.";

        try {
            const errorData =
                await response.json();

            if (errorData.detail) {
                if (
                    typeof errorData.detail ===
                    "string"
                ) {
                    message = errorData.detail;
                }
            }
        } catch {
            // Keep the default error message.
        }

        throw new Error(message);
    }

    return response.json();
}