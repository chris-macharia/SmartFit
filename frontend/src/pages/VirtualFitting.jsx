import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import {
    getAvailableGarments,
} from "../services/garmentService";

import {
    createVirtualFitting,
} from "../services/virtualFittingService";


/**
 * VirtualFitting
 *
 * Customer-facing page for SmartFit virtual fitting.
 *
 * Flow:
 *
 *     Customer Avatar
 *            ↓
 *     Select Garment
 *            ↓
 *     Perform Virtual Fitting
 *            ↓
 *     Backend Fitting Algorithm
 *            ↓
 *     Recommended Size + Fit Result
 */
export default function VirtualFitting() {
    const location = useLocation();
    const navigate = useNavigate();

    /*
     * Avatar and measurement information is passed
     * from the Avatar page through React Router state.
     */
    const avatar = location.state?.avatar || null;
    const measurements =
        location.state?.measurements || null;

    const [garments, setGarments] = useState([]);
    const [selectedGarmentId, setSelectedGarmentId] =
        useState("");

    const [loading, setLoading] = useState(true);
    const [fitting, setFitting] = useState(false);

    const [error, setError] = useState("");
    const [result, setResult] = useState(null);


    /**
     * Load garments available for virtual fitting.
     */
    useEffect(() => {
        async function loadGarments() {
            try {
                setLoading(true);
                setError("");

                const response =
                    await getAvailableGarments();

                if (!response.ok) {
                    let message =
                        "Failed to load available garments.";

                    try {
                        const errorData =
                            await response.json();

                        if (errorData.detail) {
                            message =
                                typeof errorData.detail ===
                                "string"
                                    ? errorData.detail
                                    : message;
                        }
                    } catch {
                        // Keep default message.
                    }

                    throw new Error(message);
                }

                const data =
                    await response.json();

                setGarments(data);
            } catch (err) {
                setError(
                    err.message ||
                    "Failed to load available garments."
                );
            } finally {
                setLoading(false);
            }
        }

        loadGarments();
    }, []);


    /**
     * Perform the virtual fitting using the
     * selected garment and customer's avatar.
     */
    async function handleVirtualFitting() {
        setError("");
        setResult(null);

        if (!avatar?.avatar_id) {
            setError(
                "No avatar is available. Please generate your avatar first."
            );
            return;
        }

        if (!selectedGarmentId) {
            setError(
                "Please select a garment before performing the fitting."
            );
            return;
        }

        try {
            setFitting(true);

            const fittingResult =
                await createVirtualFitting(
                    selectedGarmentId,
                    avatar.avatar_id
                );

            setResult(fittingResult);
        } catch (err) {
            setError(
                err.message ||
                "Unable to perform virtual fitting."
            );
        } finally {
            setFitting(false);
        }
    }


    /**
     * Return to the avatar page.
     */
    function handleBackToAvatar() {
        navigate("/avatar", {
            state: {
                avatar,
                measurements,
            },
        });
    }


    /*
     * The virtual fitting requires a generated avatar.
     */
    if (!avatar?.avatar_id) {
        return (
            <div className="page-container">
                <div className="page-header">
                    <h1>Virtual Fitting</h1>
                    <p>
                        Use your SmartFit avatar to find
                        the most suitable garment size.
                    </p>
                </div>

                <div className="dashboard-card">
                    <h2>Avatar Required</h2>

                    <p>
                        You need to generate your SmartFit
                        avatar before performing a virtual
                        fitting.
                    </p>

                    <button
                        type="button"
                        className="primary-button"
                        onClick={() =>
                            navigate("/avatar")
                        }
                    >
                        Go to Avatar
                    </button>
                </div>
            </div>
        );
    }


    return (
        <div className="page-container">

            {/* Page heading */}
            <div className="page-header">
                <h1>Virtual Fitting</h1>

                <p>
                    Select a garment to compare it with
                    your SmartFit body measurements.
                </p>
            </div>


            {/* Customer measurement summary */}
            {measurements && (
                <section className="dashboard-card">
                    <h2>Your Measurements</h2>

                    <div className="measurement-grid">

                        {measurements.height !== null &&
                            measurements.height !==
                                undefined && (
                                <div>
                                    <strong>
                                        Height
                                    </strong>

                                    <span>
                                        {measurements.height}
                                        {" "}cm
                                    </span>
                                </div>
                            )}

                        {measurements.chest !== null &&
                            measurements.chest !==
                                undefined && (
                                <div>
                                    <strong>
                                        Chest
                                    </strong>

                                    <span>
                                        {measurements.chest}
                                        {" "}cm
                                    </span>
                                </div>
                            )}

                        {measurements.waist !== null &&
                            measurements.waist !==
                                undefined && (
                                <div>
                                    <strong>
                                        Waist
                                    </strong>

                                    <span>
                                        {measurements.waist}
                                        {" "}cm
                                    </span>
                                </div>
                            )}

                        {measurements.hips !== null &&
                            measurements.hips !==
                                undefined && (
                                <div>
                                    <strong>
                                        Hips
                                    </strong>

                                    <span>
                                        {measurements.hips}
                                        {" "}cm
                                    </span>
                                </div>
                            )}

                        {measurements.shoulder_width !==
                            null &&
                            measurements.shoulder_width !==
                                undefined && (
                                <div>
                                    <strong>
                                        Shoulder Width
                                    </strong>

                                    <span>
                                        {
                                            measurements.shoulder_width
                                        }
                                        {" "}cm
                                    </span>
                                </div>
                            )}

                        {measurements.inseam !== null &&
                            measurements.inseam !==
                                undefined && (
                                <div>
                                    <strong>
                                        Inseam
                                    </strong>

                                    <span>
                                        {measurements.inseam}
                                        {" "}cm
                                    </span>
                                </div>
                            )}

                    </div>
                </section>
            )}


            {/* Garment selection */}
            <section className="dashboard-card">
                <h2>Select a Garment</h2>

                <p>
                    Choose a garment registered by a
                    retailer.
                </p>

                {loading && (
                    <p>
                        Loading available garments...
                    </p>
                )}

                {!loading &&
                    garments.length === 0 && (
                        <p>
                            No garments are currently
                            available for virtual fitting.
                        </p>
                    )}

                {!loading &&
                    garments.length > 0 && (
                        <div className="garment-selection-grid">

                            {garments.map((garment) => (
                                <button
                                    key={
                                        garment.garment_id
                                    }
                                    type="button"
                                    className={
                                        selectedGarmentId ===
                                        garment.garment_id
                                            ? "garment-selection-card selected"
                                            : "garment-selection-card"
                                    }
                                    onClick={() =>
                                        setSelectedGarmentId(
                                            garment.garment_id
                                        )
                                    }
                                >
                                    <h3>
                                        Garment
                                    </h3>

                                    <div>
                                        <span>
                                            Chest Width
                                        </span>
                                        <strong>
                                            {
                                                garment.chest_width
                                            }
                                            {" "}cm
                                        </strong>
                                    </div>

                                    <div>
                                        <span>
                                            Waist Width
                                        </span>
                                        <strong>
                                            {
                                                garment.waist_width
                                            }
                                            {" "}cm
                                        </strong>
                                    </div>

                                    <div>
                                        <span>
                                            Hip Width
                                        </span>
                                        <strong>
                                            {
                                                garment.hip_width
                                            }
                                            {" "}cm
                                        </strong>
                                    </div>

                                    <div>
                                        <span>
                                            Shoulder Width
                                        </span>
                                        <strong>
                                            {
                                                garment.shoulder_width
                                            }
                                            {" "}cm
                                        </strong>
                                    </div>

                                    <div>
                                        <span>
                                            Inseam
                                        </span>
                                        <strong>
                                            {
                                                garment.inseam
                                            }
                                            {" "}cm
                                        </strong>
                                    </div>

                                </button>
                            ))}

                        </div>
                    )}
            </section>


            {/* Error message */}
            {error && (
                <div className="error-message">
                    {error}
                </div>
            )}


            {/* Perform fitting */}
            <section className="dashboard-card">
                <h2>Perform Fitting</h2>

                <p>
                    Your avatar and selected garment will
                    be evaluated by the SmartFit virtual
                    fitting algorithm.
                </p>

                <button
                    type="button"
                    className="primary-button"
                    onClick={handleVirtualFitting}
                    disabled={
                        fitting ||
                        !selectedGarmentId ||
                        loading ||
                        garments.length === 0
                    }
                >
                    {fitting
                        ? "Performing Fitting..."
                        : "Perform Virtual Fitting"}
                </button>

                <button
                    type="button"
                    className="secondary-button"
                    onClick={handleBackToAvatar}
                >
                    Back to Avatar
                </button>
            </section>


            {/* Fitting result */}
            {result && (
                <section className="dashboard-card virtual-fitting-result">

                    <h2>
                        Virtual Fitting Result
                    </h2>

                    <div className="fitting-result-grid">

                        <div>
                            <span>
                                Recommended Size
                            </span>

                            <strong>
                                {
                                    result.recommended_size
                                }
                            </strong>
                        </div>

                        <div>
                            <span>
                                Fit Result
                            </span>

                            <strong>
                                {result.fit_result}
                            </strong>
                        </div>

                    </div>

                    <p>
                        This recommendation is based on
                        the body measurements extracted for
                        your SmartFit avatar and the selected
                        garment measurements.
                    </p>

                </section>
            )}

        </div>
    );
}