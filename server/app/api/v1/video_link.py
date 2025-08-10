import traceback
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.authentication.jwt.oauth2 import get_current_user
from app.authentication.models import User
from app.config import get_db, get_logger, youtube_embeded, youtube_key
from app.repository import UserRepository, VideoLinkRepository
from app.schema import (
    LinkResponse,
    VideoLinkFileResponse,
    VideoLinkRegister,
    VideoLinkResponse,
    VideoLinkWithMetadata,
    VideoMetadata,
)
from app.utils import (
    extract_file_link,
    extract_youtube_link_id,
    fetch_youtube_video_metadata,
)

logger = get_logger("[api/v1/video_link]")
router = APIRouter()


@router.get("/videos", response_model=LinkResponse)
async def get_all_links(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Retrieve all video links associated with the current authenticated user.
    This endpoint fetches all video links stored for the user identified by the current authentication context.
    It returns a structured response containing metadata for each video link, including title, description,
    publication date, channel title, thumbnail URL, and embedded URL. If no links are found, an empty list is returned.

     Args:
        current_user (User): The currently authenticated user, injected by dependency.
        db (AsyncSession): The asynchronous database session, injected by dependency.

    Returns:
        LinkResponse: A response object containing the API version, status code, list of video links with metadata,
                      the source of the links, uploader's email, and a message.

    Raises:
        HTTPException:
            - 401 Unauthorized if the user is not authenticated.
            - 500 Internal Server Error for unexpected errors during processing.
    Note:
        - The 'source' field in the response will be set to the unique source if all links share the same source,
          otherwise it will be set to "mixed".
        - All exceptions are logged for debugging purposes.
    """
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
                version="v1",
                status=status.HTTP_200_OK,
                links=[],
                source="manual",
                uploader=email,
                message="No links found",
            )

        sources = {link.source for link in result}
        if len(sources) == 1:
            response_source = sources.pop()
        else:
            response_source = "mixed"

        response_links = []
        for link in result:
            metadata_obj = VideoMetadata(
                etag=None,
                id=link.id,
                title=link.title,
                description=link.description,
                published_at=(
                    link.uploaded_at.isoformat() if link.uploaded_at else None
                ),
                channel_title=link.channel_title,
                thumbnail_url=link.thumbnail_url,
                embedded_url=(
                    f"{youtube_embeded}/{link.video_id}" if link.video_id else None
                ),
                uploaded_at=(
                    link.uploaded_at.isoformat() if link.uploaded_at else None
                ),
            )
            response_links.append(
                VideoLinkWithMetadata(url=link.url, metadata=metadata_obj)
            )

        return LinkResponse(
            version="v1",
            status=status.HTTP_200_OK,
            links=response_links,
            source=response_source,
            uploader=email,
            message="Response successfully generated",
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
    """
    Handles the creation of new video links for the current user.

    This endpoint receives a list of video URLs, checks for duplicates, fetches YouTube metadata for new links,
    and stores them in the database. If a link already exists for the user, it is skipped. For each new link,
    YouTube metadata is fetched (if possible) and included in the response. The response contains the status,
    uploader information, and details about the processed links.

    Args:
        data (VideoLinkRegister): The payload containing a list of video URLs to register.
        db (AsyncSession, optional): The database session dependency.
        current_user (User, optional): The currently authenticated user dependency.

    Returns:
        VideoLinkResponse: An object containing the status, uploader, processed links, and a message.

    Raises:
        HTTPException: If the user credentials are invalid or if an internal server error occurs.
    """

    try:
        uploader_email = getattr(current_user, "email", None)
        if not uploader_email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        repo = VideoLinkRepository(db)

        unique_input_links = list(set(data.links))

        existing_links = await repo.get_existing_links(
            current_user.id, unique_input_links
        )

        new_links = list(set(unique_input_links) - set(existing_links))

        if not new_links:
            return VideoLinkResponse(
                version="v1",
                status=status.HTTP_200_OK,
                links=[],
                source="manual",
                uploader=uploader_email,
                message="Links are Already exists",
            )

        link_payloads = []

        for url in new_links:
            item: dict = {"url": url}

            vid = extract_youtube_link_id(url)
            if not vid:
                logger.info("Could not extract video id from url: %s", url)
                link_payloads.append(item)
                continue

            meta = None
            try:
                meta = fetch_youtube_video_metadata(vid, youtube_key)
            except Exception as exc:
                logger.error("Exception fetching metadata for %s: %s", vid, exc)
                meta = None

            if meta:
                item.update(
                    {
                        "video_id": meta.get("video_id"),
                        "title": meta.get("title"),
                        "description": meta.get("description"),
                        "channel_title": meta.get("channel_title"),
                        "thumbnail_url": meta.get("thumbnail_url"),
                        "duration_seconds": meta.get("duration_seconds"),
                        "view_count": meta.get("view_count"),
                        "like_count": meta.get("like_count"),
                        "comment_count": meta.get("comment_count"),
                        "tags": meta.get("tags"),
                    }
                )
            else:
                item.update({"video_id": vid})

            link_payloads.append(item)

        created = await repo.create_video_link(
            current_user.id, link_payloads, source="manual"
        )

        response_links = []
        for created_row in created:
            vid = getattr(created_row, "video_id", None)
            metadata_obj = None
            if vid:
                metadata_obj = VideoMetadata(
                    id=getattr(created_row, "id", None),
                    etag=getattr(created_row, "etag", None),
                    title=getattr(created_row, "title", None),
                    description=getattr(created_row, "description", None),
                    published_at=getattr(created_row, "published_at", None),
                    channel_title=getattr(created_row, "channel_title", None),
                    thumbnail_url=getattr(created_row, "thumbnail_url", None),
                    uploaded_at=getattr(created_row, "uploaded_at", None),
                    embedded_url=(f"{youtube_embeded}/{vid}" if vid else None),
                )

            response_links.append(
                {"url": getattr(created_row, "url"), "metadata": metadata_obj}
            )

        return VideoLinkResponse(
            version="v1",
            status=status.HTTP_200_OK,
            links=response_links,
            source="manual",
            uploader=uploader_email,
            message="Link has been uploaded sucessfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Link creation Error (manual): %s\n%s", e, traceback.format_exc())
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
    """
    Handles the upload and processing of files containing video links.

    This endpoint allows users to upload one or more files, extracts video links from the files,
    checks for duplicates, fetches YouTube metadata for new links, and stores unique video links
    in the database. Returns a response with the status, uploader information, and details about
    the processed links.

    Args:
        files (List[UploadFile]): List of files uploaded by the user, each containing video links.
        db (AsyncSession): Database session dependency for database operations.
        current_user: The currently authenticated user, injected via dependency.

    Returns:
        VideoLinkFileResponse: A response object containing the status, uploader, and processed links,
        or a message if no new links were found.

    Raises:
        HTTPException: If a file is too large, if link extraction fails, or if an internal error occurs.

    Note:
        - Maximum allowed file size is 5 MB.
        - Only unique links not already present in the system are processed and stored.
        - YouTube metadata is fetched for each valid link, if possible.
    """
    MAX_FILE_SIZE = 5 * 1024 * 1024
    all_extracted_links = []
    repo = VideoLinkRepository(db)

    try:

        user_email = current_user.email
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
                uploader=user_email,
                message="Links already exist in the system",
            )

        link_payloads = []

        for url in unique_links:
            item: dict = {"url": url}

            vid = extract_youtube_link_id(url)
            if not vid:
                logger.info("Could not extract video id from url: %s", url)
                link_payloads.append(item)
                continue

            meta = None
            try:
                meta = fetch_youtube_video_metadata(vid, youtube_key)
            except Exception as exc:
                logger.error("Exception fetching metadata for %s: %s", vid, exc)
                meta = None

            if meta:
                item.update(
                    {
                        "video_id": meta.get("video_id"),
                        "title": meta.get("title"),
                        "description": meta.get("description"),
                        "channel_title": meta.get("channel_title"),
                        "thumbnail_url": meta.get("thumbnail_url"),
                        "duration_seconds": meta.get("duration_seconds"),
                        "view_count": meta.get("view_count"),
                        "like_count": meta.get("like_count"),
                        "comment_count": meta.get("comment_count"),
                        "tags": meta.get("tags"),
                    }
                )
            else:
                item.update({"video_id": vid})

            link_payloads.append(item)

        created = await repo.create_video_link(
            current_user.id, link_payloads, source="file"
        )

        response_links = []
        for created_row in created:
            vid = getattr(created_row, "video_id", None)
            metadata_obj = None
            if vid:
                metadata_obj = VideoMetadata(
                    id=getattr(created_row, "id", None),
                    title=getattr(created_row, "title", None),
                    description=getattr(created_row, "description", None),
                    channel_title=getattr(created_row, "channel_title", None),
                    thumbnail_url=getattr(created_row, "thumbnail_url", None),
                    uploaded_at=getattr(created_row, "uploaded_at", None),
                    embedded_url=(f"{youtube_embeded}/{vid}" if vid else None),
                )

            response_links.append(
                {"url": getattr(created_row, "url"), "metadata": metadata_obj}
            )
        logger.info("Link has been uploaded sucessfully")
        return VideoLinkFileResponse(
            version="v1",
            status=status.HTTP_200_OK,
            links=response_links,
            source="file",
            uploader=user_email,
            message="Link has been uploaded sucessfully",
        )

    except Exception as e:
        logger.error(f"Link creation Error (manual) : {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.delete("/videos-links/{id}", status_code=status.HTTP_200_OK)
async def delete_video_link(
    id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a specific video link by its database ID for the current user.

    Args:
        id (int): The unique identifier of the video link to be deleted.
        current_user (User, optional): The currently authenticated user, injected by dependency.
        db (AsyncSession, optional): The asynchronous database session, injected by dependency.

    Raises:
        HTTPException: If the video link is not found or not owned by the current user,
                       raises a 404 Not Found error.

    Returns:
        dict: A response dictionary containing the API version, HTTP status code,
              and a success message upon successful deletion.
    """

    repo = VideoLinkRepository(db)
    deleted = await repo.delete_links(current_user.id, id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video link not found or not owned by the user",
        )

    return {
        "version": "v1",
        "status": status.HTTP_200_OK,
        "message": "Video link deleted successfully",
    }
