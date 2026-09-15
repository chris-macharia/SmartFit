import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { getAvailableGarments } from "../services/garmentService";
import { createVirtualFitting } from "../services/virtualFittingService";


/**
 * VirtualFitting
 *
 * Customer-facing virtual fitting page.
 *
 * Workflow:
 *
 *     SmartFit Profile
 *            ↓
 *     Select Garment
 *            ↓
 *     Perform Fitting
 *            ↓
 *     View Fitting Result
 *
 * The page uses the existing Milestone 8 backend
 * virtual fitting API.
 */
export default function VirtualFitting() {
    const location = useLocation();
    const navigate = useNavigate();

    /*
     * Avatar and measurement information are passed
     * from the Avatar page through React Router state.
     */
    const avatar = location.state?.avatar || null;
    const measurements = location.state?.measurements || null;

    const [garments, setGarments] = useState([]);
    const [selectedGarmentId, setSelectedGarmentId] =
        useState("");

    const [loading, setLoading] = useState(true);
    const [fitting, setFitting] = useState(false);

    const [error, setError] = useState("");
    const [result, setResult] = useState(null);


    /**
     * Load garments that retailers have made
     * available for customer virtual fitting.
     */
    useEffect(() => {
        async function loadGarments() {
            try {
                setLoading(true);
                setError("");

                const response = await getAvailableGarments();

                if (!response.ok) {
                    let message =
                        "Failed to load available garments.";

                    try {
                        const errorData = await response.json();

                        if (typeof errorData.detail === "string") {
                            message = errorData.detail;
                        }
                    } catch {
                        // Keep the default message.
                    }

                    throw new Error(message);
                }

                const data = await response.json();

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
     * Return a display-friendly measurement value.
     */
    function formatMeasurement(value) {
        if (value === null || value === undefined) {
            return "Not available";
        }

        return `${value} cm`;
    }


    /**
     * Get the currently selected garment.
     */
    const selectedGarment = garments.find(
        (garment) =>
            garment.garment_id === selectedGarmentId
    );


    /**
     * Perform the virtual fitting.
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
     * Return to the generated avatar page.
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
     * Virtual fitting requires a generated avatar.
     */
    if (!avatar?.avatar_id) {
        return (
            <main className="virtual-fitting-page">
                <div className="virtual-fitting-header">
                    <span className="section-label">
                        SMARTFIT
                    </span>

                    <h1>Virtual Fitting</h1>

                    <p>
                        Compare your SmartFit profile with
                        retailer garments and receive an
                        initial fit recommendation.
                    </p>
                </div>

                <section className="virtual-fitting-card avatar-required-card">
                    <div className="virtual-fitting-status-icon">
                        !
                    </div>

                    <div>
                        <h2>Avatar Required</h2>

                        <p>
                            Generate your SmartFit avatar before
                            starting a virtual fitting.
                        </p>

                        <button
                            type="button"
                            className="primary-button"
                            onClick={() => navigate("/avatar")}
                        >
                            Go to Avatar
                        </button>
                    </div>
                </section>
            </main>
        );
    }


    return (
        <main className="virtual-fitting-page">

            {/* =====================================================
                PAGE HEADER
                ===================================================== */}

            <header className="virtual-fitting-header">
                <span className="section-label">
                    SMARTFIT VIRTUAL FITTING
                </span>

                <h1>Virtual Fitting</h1>

                <p>
                    Compare your SmartFit body measurements
                    with available retailer garments to find
                    the most suitable fit.
                </p>
            </header>


            {/* =====================================================
                WORKSPACE
                ===================================================== */}

            <div className="virtual-fitting-workspace">

                {/* =================================================
                    SMARTFIT PROFILE
                    ================================================= */}

                <section className="virtual-fitting-card profile-panel">

                    <div className="virtual-fitting-card-header">
                        <div>
                            <span className="section-label">
                                STEP 01
                            </span>

                            <h2>Your SmartFit Profile</h2>
                        </div>

                        <span className="profile-ready-badge">
                            Ready
                        </span>
                    </div>

                    <p className="virtual-fitting-card-description">
                        These are the measurements currently
                        available for your virtual fitting.
                    </p>

                    <div className="fitting-measurement-grid">

                        <div className="fitting-measurement">
                            <span>Height</span>
                            <strong>
                                {formatMeasurement(
                                    measurements?.height
                                )}
                            </strong>
                        </div>

                        <div className="fitting-measurement">
                            <span>Chest</span>
                            <strong>
                                {formatMeasurement(
                                    measurements?.chest
                                )}
                            </strong>
                        </div>

                        <div className="fitting-measurement">
                            <span>Waist</span>
                            <strong>
                                {formatMeasurement(
                                    measurements?.waist
                                )}
                            </strong>
                        </div>

                        <div className="fitting-measurement">
                            <span>Hips</span>
                            <strong>
                                {formatMeasurement(
                                    measurements?.hips
                                )}
                            </strong>
                        </div>

                        <div className="fitting-measurement">
                            <span>Shoulder Width</span>
                            <strong>
                                {formatMeasurement(
                                    measurements?.shoulder_width
                                )}
                            </strong>
                        </div>

                        <div className="fitting-measurement">
                            <span>Inseam</span>
                            <strong>
                                {formatMeasurement(
                                    measurements?.inseam
                                )}
                            </strong>
                        </div>

                    </div>

                    <div className="profile-note">
                        <strong>Measurement note</strong>

                        <p>
                            The current prototype uses the
                            measurements successfully extracted
                            from your uploaded body video.
                            Unavailable measurements are ignored
                            during fitting.
                        </p>
                    </div>

                </section>


                {/* =================================================
                    GARMENT SELECTION
                    ================================================= */}

                <section className="virtual-fitting-card garment-panel">

                    <div className="virtual-fitting-card-header">
                        <div>
                            <span className="section-label">
                                STEP 02
                            </span>

                            <h2>Select a Garment</h2>
                        </div>

                        {!loading && garments.length > 0 && (
                            <span className="garment-count">
                                {garments.length} available
                            </span>
                        )}
                    </div>

                    <p className="virtual-fitting-card-description">
                        Select one of the garments registered
                        by SmartFit retailers.
                    </p>


                    {loading && (
                        <div className="fitting-loading">
                            <span className="fitting-spinner" />

                            <span>
                                Loading available garments...
                            </span>
                        </div>
                    )}


                    {!loading && garments.length === 0 && (
                        <div className="empty-garment-state">
                            <strong>
                                No garments available
                            </strong>

                            <p>
                                Retailer garments will appear
                                here when they are available
                                for virtual fitting.
                            </p>
                        </div>
                    )}


                    {!loading && garments.length > 0 && (
                        <div className="garment-scroll-container">

                            <div className="garment-selection-grid">

                                {garments.map((garment, index) => {
                                    const isSelected =
                                        selectedGarmentId ===
                                        garment.garment_id;

                                    return (
                                        <button
                                            key={
                                                garment.garment_id
                                            }
                                            type="button"
                                            className={
                                                isSelected
                                                    ? "garment-selection-card selected"
                                                    : "garment-selection-card"
                                            }
                                            onClick={() =>
                                                setSelectedGarmentId(
                                                    garment.garment_id
                                                )
                                            }
                                            aria-pressed={isSelected}
                                        >

                                            <div className="garment-card-header">
                                                <span className="garment-number">
                                                    {String(index + 1).padStart(
                                                        2,
                                                        "0"
                                                    )}
                                                </span>

                                                {isSelected && (
                                                    <span className="garment-selected-indicator">
                                                        ✓ Selected
                                                    </span>
                                                )}
                                            </div>

                                            <h3>
                                                Retailer Garment
                                            </h3>

                                            <div className="garment-measurements">

                                                <div>
                                                    <span>
                                                        Chest Width
                                                    </span>

                                                    <strong>
                                                        {formatMeasurement(
                                                            garment.chest_width
                                                        )}
                                                    </strong>
                                                </div>

                                                <div>
                                                    <span>
                                                        Waist Width
                                                    </span>

                                                    <strong>
                                                        {formatMeasurement(
                                                            garment.waist_width
                                                        )}
                                                    </strong>
                                                </div>

                                                <div>
                                                    <span>
                                                        Hip Width
                                                    </span>

                                                    <strong>
                                                        {formatMeasurement(
                                                            garment.hip_width
                                                        )}
                                                    </strong>
                                                </div>

                                                <div>
                                                    <span>
                                                        Shoulder Width
                                                    </span>

                                                    <strong>
                                                        {formatMeasurement(
                                                            garment.shoulder_width
                                                        )}
                                                    </strong>
                                                </div>

                                                <div>
                                                    <span>
                                                        Inseam
                                                    </span>

                                                    <strong>
                                                        {formatMeasurement(
                                                            garment.inseam
                                                        )}
                                                    </strong>
                                                </div>

                                            </div>

                                        </button>
                                    );
                                })}

                            </div>

                        </div>
                    )}

                </section>

            </div>


            {/* =====================================================
                SELECTED GARMENT SUMMARY
                ===================================================== */}

            {selectedGarment && (
                <section className="selected-garment-summary">

                    <div>
                        <span className="section-label">
                            SELECTED GARMENT
                        </span>

                        <h2>Garment {String(
                            garments.findIndex(
                                (garment) =>
                                    garment.garment_id ===
                                    selectedGarmentId
                            ) + 1
                        ).padStart(2, "0")}</h2>

                        <p>
                            This garment will be compared
                            against your available body
                            measurements.
                        </p>
                    </div>

                    <div className="selected-garment-action">
                        <button
                            type="button"
                            className="primary-button"
                            onClick={handleVirtualFitting}
                            disabled={fitting}
                        >
                            {fitting
                                ? "Performing Fitting..."
                                : "Perform Virtual Fitting"}
                        </button>
                    </div>

                </section>
            )}


            {/* =====================================================
                ERROR
                ===================================================== */}

            {error && (
                <div
                    className="error-message virtual-fitting-error"
                    role="alert"
                >
                    {error}
                </div>
            )}


            {/* =====================================================
                FITTING RESULT
                ===================================================== */}

            {result && (
                <section className="virtual-fitting-result">

                    <div className="result-header">
                        <span className="section-label">
                            STEP 03
                        </span>

                        <h2>Virtual Fitting Result</h2>

                        <p>
                            Your garment has been evaluated
                            against the body measurements
                            currently available in your
                            SmartFit profile.
                        </p>
                    </div>


                    <div className="fitting-result-grid">

                        <div className="fitting-result-item">

                            <span>
                                Recommended Size
                            </span>

                            <strong className="recommended-size">
                                {result.recommended_size}
                            </strong>

                        </div>


                        <div className="fitting-result-item">

                            <span>
                                Fit Result
                            </span>

                            <strong
                                className={
                                    `fit-result fit-result-${String(
                                        result.fit_result || ""
                                    ).toLowerCase().replace(
                                        /\s+/g,
                                        "-"
                                    )}`
                                }
                            >
                                {result.fit_result}
                            </strong>

                        </div>

                    </div>


                    <div className="result-explanation">
                        <strong>
                            How this result is determined
                        </strong>

                        <p>
                            SmartFit compares the available
                            body and garment measurements.
                            Measurements that are not currently
                            available are excluded from the
                            comparison.
                        </p>
                    </div>

                </section>
            )}


            {/* =====================================================
                NAVIGATION
                ===================================================== */}

            <div className="virtual-fitting-navigation">

                <button
                    type="button"
                    className="secondary-button"
                    onClick={handleBackToAvatar}
                >
                    ← Back to Avatar
                </button>

            </div>

        </main>
    );
}