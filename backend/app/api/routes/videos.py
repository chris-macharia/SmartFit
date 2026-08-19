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
Newly uploaded videos are processed in the background and transition
through uploaded, processing, completed, or failed states.
"""

import uuid
from pathlib import Path

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
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
from app.services.video_processor import process_video


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

# Maximum accepted upload size: 500 MB. The backend enforces this limit
# while streaming the file because client-side validation can be bypassed.
MAX_VIDEO_SIZE_BYTES = 500 * 1024 * 1024


# ============================================================
# CREATE - Upload Video
# ============================================================

@router.post(
    "/",
    response_model=VideoResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_height_cm: float = Form(...),
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
    5. Queued for background measurement processing.
    """

    # --------------------------------------------------------
    # Validate the supplied measurement calibration data.
    # --------------------------------------------------------

    # A normal camera video has no inherent centimetre scale. SmartFit
    # therefore requires a plausible user-declared height before it can
    # estimate measurements from normalized pose landmarks.
    if not 100 <= user_height_cm <= 250:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Height must be between 100 cm and 250 cm.",
        )

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
        bytes_written = 0

        with file_path.open("wb") as buffer:

            # Read the uploaded file in 1 MB chunks.
            #
            # This prevents large videos from being loaded
            # completely into memory.
            while chunk := await file.read(1024 * 1024):
                bytes_written += len(chunk)

                # Stop before writing beyond SmartFit's maximum. The partial
                # file is removed below so oversized uploads leave no orphaned
                # data in the video storage directory.
                if bytes_written > MAX_VIDEO_SIZE_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="Video files must not exceed 500 MB.",
                    )

                buffer.write(chunk)

    except HTTPException:
        if file_path.exists():
            file_path.unlink()

        raise

    except Exception as exc:
        if file_path.exists():
            file_path.unlink()

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
        user_height_cm=user_height_cm,
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

    # Start processing after the upload response is prepared. The background
    # service creates its own database session because this request session
    # will be closed once FastAPI returns the response.
    background_tasks.add_task(process_video, video.video_id)

    # Return the newly created video. Its processing state will transition
    # independently from "uploaded" to "processing" and then a final state.
    return video


# ============================================================
# READ - Retrieve Video Status
# ============================================================

@router.get(
    "/{video_id}",
    response_model=VideoResponse,
    status_code=status.HTTP_200_OK,
)
def get_video(
    video_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return one video owned by the authenticated user.

    The frontend can call this endpoint to poll processing status without
    being able to inspect another user's uploaded body video.
    """

    video = (
        db.query(Video)
        .filter(
            Video.video_id == video_id,
            Video.user_id == current_user.user_id,
        )
        .first()
    )

    if video is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video not found.",
        )

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
