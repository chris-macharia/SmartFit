"""
Main entry point for the SmartFit FastAPI application.

This module creates the FastAPI application instance and
registers the central API router.
"""

from fastapi import FastAPI

from app.api.router import api_router


# Create the SmartFit FastAPI application.
#
# The metadata below is displayed in the automatically
# generated Swagger/OpenAPI documentation.
app = FastAPI(
    title="SmartFit API",
    description="Backend API for the SmartFit Virtual Fitting System",
    version="1.0.0"
)


# Register the central API router.
#
# All SmartFit API endpoints will be organized under the
# central API router. Individual route modules will be
# connected to this router as development continues.
app.include_router(api_router)


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
        "status": "running"
    }