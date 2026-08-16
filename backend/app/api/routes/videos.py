"""
Video API routes for SmartFit.

This module provides endpoints for creating, retrieving,
and deleting videos belonging to the authenticated SmartFit user.

Current video operations:

1. Create/upload a video.
2. Delete an existing video.

SmartFit does not provide an update/replace operation for videos.
If a user records or selects an incorrect video, the existing video
can be deleted and a new video can be uploaded instead.

The computer-vision processing pipeline will be connected later.
For now, newly uploaded videos receive the status "uploaded".
"""

import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.video import Video
from app.schemas.video import VideoResponse


# ============================================================
# Router Configuration
# ============================================================

# All video endpoints are available under:
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

# Directory where uploaded videos are stored.
#
# Example:
#
#     backend/uploads/videos/
#
VIDEO_UPLOAD_DIR = Path("uploads/videos")

# Create the directory automatically if it does not exist.
VIDEO_UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# Allowed Video Types
# ============================================================

# MIME types accepted by SmartFit.
#
# MP4     -> video/mp4
# MOV     -> video/quicktime
# WebM    -> video/webm
#
ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/webm",
}


# ============================================================
# CREATE - Upload Video
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
    Upload a new body video for the authenticated user.

    The user's identity comes from the JWT rather than from
    information supplied by the frontend.

    The uploaded video is:

    1. Validated.
    2. Saved to the video upload directory.
    3. Stored in the database.
    4. Assigned the initial processing status "uploaded".

    The computer-vision processing pipeline will later pick up
    the video for measurement and avatar generation.
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

    # Do not use the original filename directly.
    #
    # UUID-based filenames:
    #
    # - Prevent filename collisions.
    # - Avoid trusting user-provided filenames.
    # - Make stored files uniquely identifiable.
    #
    file_extension = Path(
        file.filename or ""
    ).suffix.lower()

    # If no extension was supplied, use MP4 as the default.
    if not file_extension:
        file_extension = ".mp4"

    # Generate the UUID that will also be used as the
    # database video_id.
    video_id = uuid.uuid4()

    filename = f"{video_id}{file_extension}"

    file_path = VIDEO_UPLOAD_DIR / filename

    # --------------------------------------------------------
    # Save the uploaded video.
    # --------------------------------------------------------

    try:
        with file_path.open("wb") as buffer:

            # Read the uploaded file in 1 MB chunks.
            #
            # This prevents large videos from being loaded
            # completely into memory.
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the uploaded video.",
        ) from exc

    finally:
        # Always close the uploaded file.
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

    # Return the newly created video.
    return video


# ============================================================
# DELETE - Delete Video
# ============================================================

@router.delete(
    "/{video_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_video(
    video_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete an existing video belonging to the authenticated user.

    Both the database record and the physical video file are
    removed.

    A user cannot delete another user's video.
    """

    # --------------------------------------------------------
    # Find the video belonging to the authenticated user.
    # --------------------------------------------------------

    video = (
        db.query(Video)
        .filter(
            Video.video_id == video_id,
            Video.user_id == current_user.user_id,
        )
        .first()
    )

    # --------------------------------------------------------
    # Make sure the video exists and belongs to the user.
    # --------------------------------------------------------

    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found.",
        )

    # Keep the physical file path before deleting the
    # database record.
    file_path = Path(video.video_path)

    # --------------------------------------------------------
    # Delete the database record.
    # --------------------------------------------------------

    try:
        db.delete(video)
        db.commit()

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete the video record.",
        ) from exc

    # --------------------------------------------------------
    # Delete the physical video file.
    # --------------------------------------------------------

    try:

        if file_path.exists():
            file_path.unlink()

    except Exception as exc:
        # The database record has already been deleted at this
        # point. Report the problem so the failed file deletion
        # is not hidden.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Video record deleted, but the physical file "
                "could not be removed."
            ),
        ) from exc

    # HTTP 204 responses must not contain a response body.
    return None