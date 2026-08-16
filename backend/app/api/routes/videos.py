"""
Video API routes for SmartFit.

This module provides endpoints for uploading and retrieving
videos belonging to the authenticated SmartFit user.

The video upload process currently performs the following:

1. Authenticate the user using the JWT.
2. Accept a video file from the frontend.
3. Save the file to the SmartFit upload directory.
4. Create a corresponding Video database record.
5. Return the stored video information.

The computer-vision processing pipeline will be connected
later. For now, newly uploaded videos receive the status
"uploaded".
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.video import Video
from app.schemas.video import VideoResponse


# ============================================================
# Router Configuration
# ============================================================

# All endpoints in this module will be available under:
#
#     /api/videos
#
router = APIRouter(
    prefix="/videos",
    tags=["Videos"],
)


# ============================================================
# Video Storage Configuration
# ============================================================

# Define the directory where uploaded videos will be stored.
#
# The directory is relative to the backend project directory.
#
# Example:
#
#     backend/uploads/videos/
#
VIDEO_UPLOAD_DIR = Path("uploads/videos")


# Make sure the upload directory exists when the application
# starts and this module is imported.
VIDEO_UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# Allowed Video Types
# ============================================================

# Restrict uploads to common video formats supported by
# SmartFit's planned processing pipeline.
#
# The actual computer-vision processing requirements can be
# expanded later if necessary.
ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/webm",
}


# ============================================================
# Upload Video
# ============================================================

@router.post(
    "/",
    response_model=VideoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Upload a body video for the authenticated user.

    The user's identity is obtained from the JWT rather than
    being supplied by the frontend.

    Args:
        file:
            Video file uploaded by the user.

        current_user:
            Authenticated SmartFit user obtained from the JWT.

        db:
            Database session used to create the Video record.

    Returns:
        VideoResponse:
            Information about the newly uploaded video.

    Raises:
        HTTPException:
            400 if the uploaded file type is not supported.
        HTTPException:
            500 if the file cannot be stored or the database
            record cannot be created.
    """

    # --------------------------------------------------------
    # Validate the uploaded file type.
    # --------------------------------------------------------

    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported video format. "
                "Please upload an MP4, MOV, or WebM video."
            ),
        )

    # --------------------------------------------------------
    # Generate a unique filename.
    # --------------------------------------------------------

    # We do not use the original filename directly because:
    #
    # 1. Different users may upload files with the same name.
    # 2. User-provided filenames should not be trusted.
    # 3. UUID filenames make stored files easier to identify.
    #
    file_extension = Path(file.filename or "").suffix.lower()

    if not file_extension:
        file_extension = ".mp4"

    video_id = uuid.uuid4()

    filename = f"{video_id}{file_extension}"

    file_path = VIDEO_UPLOAD_DIR / filename

    # --------------------------------------------------------
    # Save the uploaded file.
    # --------------------------------------------------------

    try:
        with file_path.open("wb") as buffer:

            # Read the uploaded file in chunks rather than
            # loading the entire video into memory at once.
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the uploaded video.",
        ) from exc

    finally:
        # Close the uploaded file after processing.
        await file.close()

    # --------------------------------------------------------
    # Create the database record.
    # --------------------------------------------------------

    video = Video(
        video_id=video_id,
        user_id=current_user.user_id,
        video_path=str(file_path),
        processing_status="uploaded",
    )

    try:
        db.add(video)
        db.commit()
        db.refresh(video)

    except Exception as exc:
        # If the database operation fails, remove the physical
        # file so that we do not leave an orphaned video behind.
        if file_path.exists():
            file_path.unlink()

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create the video record.",
        ) from exc

    # Return the database record using VideoResponse.
    return video