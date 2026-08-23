/**
 * SmartFit Garments Page
 *
 * This page allows authenticated retailer accounts to
 * register and view their garments.
 *
 * The current version only handles the measurement fields
 * represented by the SmartFit Garment database model:
 *
 * - Chest width
 * - Waist width
 * - Hip width
 * - Shoulder width
 * - Inseam
 *
 * Additional garment information such as:
 *
 * - garment name
 * - brand
 * - category
 * - images
 * - 3D model
 * - price
 *
 * can be added later when the backend model is expanded.
 */

import { useEffect, useState } from "react";

import {
    createGarment,
    getMyGarments,
} from "../services/garmentService";

import { useAuth } from "../context/AuthContext";


function Garments() {

    // =========================================================
    // AUTHENTICATED USER
    // =========================================================

    const {
        user,
    } = useAuth();


    // =========================================================
    // FORM STATE
    // =========================================================

    const [formData, setFormData] = useState({
        chest_width: "",
        waist_width: "",
        hip_width: "",
        shoulder_width: "",
        inseam: "",
    });


    // =========================================================
    // GARMENT STATE
    // =========================================================

    const [garments, setGarments] = useState([]);

    const [loading, setLoading] = useState(true);

    const [submitting, setSubmitting] = useState(false);

    const [error, setError] = useState("");

    const [success, setSuccess] = useState("");


    // =========================================================
    // LOAD GARMENTS
    // =========================================================

    useEffect(() => {

        async function loadGarments() {

            try {

                setLoading(true);
                setError("");

                const response = await getMyGarments();


                if (!response.ok) {

                    let message =
                        "Unable to retrieve your garments.";

                    try {

                        const errorData =
                            await response.json();

                        if (errorData.detail) {
                            message = errorData.detail;
                        }

                    } catch {
                        // Keep default message.
                    }

                    throw new Error(message);
                }


                const data = await response.json();

                setGarments(data);

            } catch (requestError) {

                console.error(
                    "Unable to load garments:",
                    requestError
                );

                setError(
                    requestError.message ||
                    "Unable to load garments."
                );

            } finally {

                setLoading(false);
            }
        }


        /*
         * Only retailers should request garment data.
         */
        if (user?.role === "retailer") {

            loadGarments();

        } else {

            setLoading(false);
        }

    }, [user]);


    // =========================================================
    // HANDLE INPUT
    // =========================================================

    function handleChange(event) {

        const {
            name,
            value,
        } = event.target;


        setFormData((previousData) => ({
            ...previousData,
            [name]: value,
        }));


        setError("");
        setSuccess("");
    }


    // =========================================================
    // FORM SUBMISSION
    // =========================================================

    async function handleSubmit(event) {

        event.preventDefault();

        setError("");
        setSuccess("");


        // -----------------------------------------------------
        // Validate measurements
        // -----------------------------------------------------

        const measurements = [
            formData.chest_width,
            formData.waist_width,
            formData.hip_width,
            formData.shoulder_width,
            formData.inseam,
        ];


        const hasInvalidMeasurement =
            measurements.some(
                (value) =>
                    value === "" ||
                    Number(value) <= 0
            );


        if (hasInvalidMeasurement) {

            setError(
                "Please enter a valid positive value for every measurement."
            );

            return;
        }


        // -----------------------------------------------------
        // Send garment to backend
        // -----------------------------------------------------

        setSubmitting(true);


        try {

            const response = await createGarment({

                chest_width:
                    Number(formData.chest_width),

                waist_width:
                    Number(formData.waist_width),

                hip_width:
                    Number(formData.hip_width),

                shoulder_width:
                    Number(formData.shoulder_width),

                inseam:
                    Number(formData.inseam),
            });


            if (!response.ok) {

                let message =
                    "Unable to register the garment.";

                try {

                    const errorData =
                        await response.json();

                    if (errorData.detail) {
                        message = errorData.detail;
                    }

                } catch {
                    // Keep default message.
                }

                throw new Error(message);
            }


            // -------------------------------------------------
            // Get the newly-created garment
            // -------------------------------------------------

            const newGarment =
                await response.json();


            /*
             * Add the new garment to the existing list
             * immediately instead of requiring a page refresh.
             */
            setGarments((previousGarments) => [
                newGarment,
                ...previousGarments,
            ]);


            // -------------------------------------------------
            // Reset form
            // -------------------------------------------------

            setFormData({
                chest_width: "",
                waist_width: "",
                hip_width: "",
                shoulder_width: "",
                inseam: "",
            });


            setSuccess(
                "Garment registered successfully."
            );

        } catch (requestError) {

            console.error(
                "Garment registration failed:",
                requestError
            );

            setError(
                requestError.message ||
                "Unable to register the garment."
            );

        } finally {

            setSubmitting(false);
        }
    }


    // =========================================================
    // ACCESS CONTROL
    // =========================================================

    /*
     * The backend also enforces retailer authorization.
     *
     * This frontend check simply prevents customers from
     * seeing a retailer-only interface.
     */
    if (user?.role !== "retailer") {

        return (
            <main className="dashboard-page">

                <section className="dashboard-header">

                    <div className="dashboard-heading">

                        <p className="section-label">
                            ACCESS RESTRICTED
                        </p>

                        <h1>
                            Retailer Access Required
                        </h1>

                        <p>
                            Garment registration is currently
                            available only to retailer accounts.
                        </p>

                    </div>

                </section>

            </main>
        );
    }


    // =========================================================
    // PAGE
    // =========================================================

    return (
        <main className="dashboard-page">


            {/* =================================================
                PAGE HEADER
                ================================================= */}

            <section className="dashboard-header">

                <div className="dashboard-heading">

                    <p className="section-label">
                        RETAILER
                    </p>

                    <h1>
                        Manage Garments
                    </h1>

                    <p>
                        Register garment measurements for
                        SmartFit virtual fitting.
                    </p>

                </div>

            </section>


            {/* =================================================
                REGISTER GARMENT
                ================================================= */}

            <section className="dashboard-section">

                <div className="section-heading">

                    <p className="section-label">
                        GARMENT REGISTRATION
                    </p>

                    <h2>
                        Add a Garment
                    </h2>

                    <p>
                        Enter the garment measurements in
                        centimetres.
                    </p>

                </div>


                <form
                    className="auth-form"
                    onSubmit={handleSubmit}
                    noValidate
                >


                    {/* Chest */}

                    <div className="form-group">

                        <label htmlFor="chest_width">
                            Chest Width (cm)
                        </label>

                        <input
                            id="chest_width"
                            name="chest_width"
                            type="number"
                            min="0"
                            step="0.01"
                            value={formData.chest_width}
                            onChange={handleChange}
                            placeholder="Enter chest width"
                        />

                    </div>


                    {/* Waist */}

                    <div className="form-group">

                        <label htmlFor="waist_width">
                            Waist Width (cm)
                        </label>

                        <input
                            id="waist_width"
                            name="waist_width"
                            type="number"
                            min="0"
                            step="0.01"
                            value={formData.waist_width}
                            onChange={handleChange}
                            placeholder="Enter waist width"
                        />

                    </div>


                    {/* Hip */}

                    <div className="form-group">

                        <label htmlFor="hip_width">
                            Hip Width (cm)
                        </label>

                        <input
                            id="hip_width"
                            name="hip_width"
                            type="number"
                            min="0"
                            step="0.01"
                            value={formData.hip_width}
                            onChange={handleChange}
                            placeholder="Enter hip width"
                        />

                    </div>


                    {/* Shoulder */}

                    <div className="form-group">

                        <label htmlFor="shoulder_width">
                            Shoulder Width (cm)
                        </label>

                        <input
                            id="shoulder_width"
                            name="shoulder_width"
                            type="number"
                            min="0"
                            step="0.01"
                            value={formData.shoulder_width}
                            onChange={handleChange}
                            placeholder="Enter shoulder width"
                        />

                    </div>


                    {/* Inseam */}

                    <div className="form-group">

                        <label htmlFor="inseam">
                            Inseam (cm)
                        </label>

                        <input
                            id="inseam"
                            name="inseam"
                            type="number"
                            min="0"
                            step="0.01"
                            value={formData.inseam}
                            onChange={handleChange}
                            placeholder="Enter inseam"
                        />

                    </div>


                    {/* =================================================
                        FEEDBACK
                        ================================================= */}

                    {error && (

                        <div
                            className="form-message error-message"
                            role="alert"
                        >
                            {error}
                        </div>

                    )}


                    {success && (

                        <div
                            className="form-message success-message"
                            role="status"
                        >
                            {success}
                        </div>

                    )}


                    {/* =================================================
                        SUBMIT
                        ================================================= */}

                    <button
                        type="submit"
                        className="primary-button auth-submit"
                        disabled={submitting}
                    >

                        {submitting
                            ? "Registering..."
                            : "Register Garment"}

                    </button>


                </form>

            </section>


            {/* =================================================
                REGISTERED GARMENTS
                ================================================= */}

            <section className="dashboard-section">

                <div className="section-heading">

                    <p className="section-label">
                        YOUR GARMENTS
                    </p>

                    <h2>
                        Registered Garments
                    </h2>

                </div>


                {loading ? (

                    <p>
                        Loading your garments...
                    </p>

                ) : garments.length === 0 ? (

                    <p>
                        You have not registered any garments yet.
                    </p>

                ) : (

                    <div className="dashboard-grid">

                        {garments.map((garment) => (

                            <div
                                key={garment.garment_id}
                                className="dashboard-card"
                            >

                                <div className="dashboard-card-icon">
                                    👕
                                </div>


                                <div className="dashboard-card-content">

                                    <h3>
                                        Garment
                                    </h3>

                                    <p>
                                        Chest:{" "}
                                        {garment.chest_width} cm
                                    </p>

                                    <p>
                                        Waist:{" "}
                                        {garment.waist_width} cm
                                    </p>

                                    <p>
                                        Hip:{" "}
                                        {garment.hip_width} cm
                                    </p>

                                    <p>
                                        Shoulder:{" "}
                                        {garment.shoulder_width} cm
                                    </p>

                                    <p>
                                        Inseam:{" "}
                                        {garment.inseam} cm
                                    </p>

                                </div>

                            </div>

                        ))}

                    </div>

                )}

            </section>

        </main>
    );
}


export default Garments;