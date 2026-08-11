"""
Main entry point for the SmartFit FastAPI application.

This module creates the FastAPI application instance,
configures application-wide middleware, and registers
the central API router.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router


# ============================================================
# FASTAPI APPLICATION
# ============================================================

# Create the SmartFit FastAPI application.
#
# The metadata below is displayed in the automatically
# generated Swagger/OpenAPI documentation.
app = FastAPI(
    title="SmartFit API",
    description="Backend API for the SmartFit Virtual Fitting System",
    version="1.0.0",
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

# CORS (Cross-Origin Resource Sharing) controls which
# frontend applications are allowed to communicate with
# this FastAPI backend from a web browser.
#
# During development, our React/Vite frontend runs on
# localhost:5173 while FastAPI runs on port 8000.
#
# Because these are different origins, the browser requires
# the backend to explicitly allow the frontend.
#
# We allow both localhost and 127.0.0.1 because browsers
# treat them as different origins even though they both
# refer to the local development machine.

allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


# Add FastAPI's CORS middleware to the application.
#
# allow_origins:
#     Specifies which frontend origins are allowed.
#
# allow_credentials:
#     Allows authentication-related information such as
#     authorization headers and cookies to be exchanged.
#
# allow_methods:
#     Allows the frontend to use all standard HTTP methods
#     such as GET, POST, PUT, PATCH, and DELETE.
#
# allow_headers:
#     Allows request headers such as Content-Type and
#     Authorization, which we will need for JWT authentication.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTER
# ============================================================

# Register the central API router.
#
# All SmartFit API endpoints are organized through this
# central router. Individual route modules are connected
# to the router as development continues.
app.include_router(api_router)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    """
    Root endpoint used to verify that the SmartFit API
    is running successfully.

    Returns:
        dict: Basic API status information.
    """

    return {
        "message": "Welcome to SmartFit API",
        "status": "running",
    }
