import traceback

from app.authentication.jwt.oauth2 import get_current_user
from app.authentication.models import User
from app.config import get_db, get_logger
from app.repository import UserRepository, VideoLinkRepository
from app.schema import VideoLinkRegister, VideoLinkResponse
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger("[api/v1/video_link]")
router = APIRouter()


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
            current_user.id, data.links
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
        logger.error(f"Link creation Error: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
