import traceback
from typing import List

from app.authentication.jwt.oauth2 import get_current_user
from app.authentication.models import User
from app.config import get_db, get_logger
from app.repository import UserRepository, VideoLinkRepository
from app.schema import (
    LinkResponse,
    VideoLinkFileResponse,
    VideoLinkRegister,
    VideoLinkResponse,
)
from app.utils import extract_file_link
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger("[api/v1/video_link]")
router = APIRouter()


@router.get("/videos", response_model=LinkResponse)
async def get_all_links(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    try:
        user_id = current_user.id
        email = current_user.email

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized access to the content",
            )

        repo = VideoLinkRepository(db)
        result = await repo.get_all_links(user_id)

        if not result:
            return LinkResponse(
                id=user_id,
                links=[],
                source="manual",
                uploader=email,
                version="v1",
                message="No links found",
                uploaded_at=None,
            )

        first_link = result[0]
        sources = {link.source for link in result}
        if len(sources) == 1:
            response_source = sources.pop()
        else:
            response_source = "mixed"

        return LinkResponse(
            id=user_id,
            links=[link.url for link in result],
            source=response_source,
            uploader=email,
            version="v1",
            message="Response successfully generated",
            uploaded_at=(
                first_link.uploaded_at.isoformat() if first_link.uploaded_at else None
            ),
        )
    except Exception as e:
        logger.error(
            f"Response creation Error (manual) : {e}\n{traceback.format_exc()}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.post(
    "/video-links", status_code=status.HTTP_200_OK, response_model=VideoLinkResponse
)
async def video_links(
    data: VideoLinkRegister,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        user_repo = UserRepository(db)
        video_link_repo = VideoLinkRepository(db)
        user_details = await user_repo.profile_details(current_user.id)
        if not user_details:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        uploader_email = user_details.email

        created_links = await video_link_repo.create_video_link(
            current_user.id, data.links, source="manual"
        )
        logger.info("Links have been uploaded successfully")

        return VideoLinkResponse(
            version="v1",
            status=status.HTTP_200_OK,
            links=[link.url for link in created_links],
            source="manual",
            uploader=uploader_email,
        )

    except Exception as e:
        logger.error(f"Link creation Error (manual) : {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.post("/video-links/files", response_model=VideoLinkFileResponse)
async def upload_links_files(
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    MAX_FILE_SIZE = 5 * 1024 * 1024
    all_extracted_links = []
    repo = VideoLinkRepository(db)

    try:

        user_id = current_user.id
        for file in files:
            file_bytes = await file.read()

            if len(file_bytes) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400, detail=f"File {file.filename} too large"
                )

            try:
                links = extract_file_link(file_bytes, file.filename)
            except ValueError as ve:
                logger.error(f"Something went wrong: {ve}\n{traceback.format_exc()}")
                raise HTTPException(status_code=400, detail=str(ve))

            if links:
                all_extracted_links.extend(links)

        if not all_extracted_links:
            return {"message": "No links found in provided files", "links": []}

        prepare_unique_links = list(set(all_extracted_links))

        existing_links = await repo.get_existing_links(
            current_user.id, prepare_unique_links
        )
        unique_links = list(set(prepare_unique_links) - set(existing_links))

        if not unique_links:
            return VideoLinkFileResponse(
                version="v1",
                status=status.HTTP_200_OK,
                links=[],
                source="file",
                uploader=current_user.id,
                message="Links already exist in the system",
            )

        created_links = await repo.create_video_link(
            current_user.id, links=unique_links, source="file"
        )
        logger.info("Links have been uploaded successfully")
        return VideoLinkFileResponse(
            version="v1",
            status=status.HTTP_200_OK,
            links=[link.url for link in created_links],
            source="file",
            uploader=user_id,
            message="Link has been uploaded",
        )

    except Exception as e:
        logger.error(f"Link creation Error (manual) : {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
