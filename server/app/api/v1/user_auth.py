import os
import shutil
import traceback
import uuid

from app.authentication.jwt.oauth2 import get_current_user
from app.authentication.jwt.token import create_access_token
from app.authentication.models import User
from app.config import get_db, get_logger
from app.config.appwrite_client import AppwriteClient
from app.repository import UserRepository
from app.schema import ProfileResponse, Token, UploadProfile, UserRegister
from app.utils import cache_response, user_cache_key
from appwrite.exception import AppwriteException
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger("[api/v1/user_auth]")
router = APIRouter()


@router.post("/register")
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    try:
        repo = UserRepository(db)
        existing_user = await repo.find_by_email(data.email)

        if existing_user:
            logger.warning(f'Warning: "User Already Exists')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already exists in the system",
            )

        await repo.create_user(data.email, data.password)
        logger.info("User registered successfully.")

        return {
            "version": "v1",
            "status": status.HTTP_200_OK,
            "message": "User has been registered successfully",
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Signup Error: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    try:
        repo = UserRepository(db)
        user = await repo.find_by_email(form_data.username)

        if not user or not repo.verify_password(form_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )

        access_token = create_access_token(user_id=user.id)
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Login Error: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@router.get("/me", response_model=ProfileResponse)
@cache_response(user_cache_key, ttl=300)
async def me(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    user = await repo.profile_details(current_user.id)
    all_links = [link.url for link in user.uploaded_links]
    return {
        "version": "v1",
        "status": status.HTTP_200_OK,
        "id": user.id,
        "email": user.email,
        "profile_img": user.profile_img,
        "is_oauth": user.is_oauth,
        "uploaded_links": len(all_links),
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }


@router.post("/upload-profile-image/", response_model=UploadProfile)
async def upload_profile_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    temp_filename = f"/tmp/{uuid.uuid4()}_{file.filename}"
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        appwrite_client = AppwriteClient()

        result = appwrite_client.create_storage(
            temp_filename=temp_filename, current_user=current_user
        )

        os.remove(temp_filename)

        preview_img = appwrite_client.getFilePreview(result)

        repo = UserRepository(db)
        image_id = await repo.get_image_id(current_user.id)
        # deleting before adding new image
        if image_id:
            await appwrite_client.delete_upload(image_id)

        updated_user = await repo.update_profile_image(
            current_user.id, str(preview_img)
        )
        if not updated_user:
            raise HTTPException(
                status_code=404, detail="User not found or update failed"
            )

        return {
            "version": "v1",
            "status": status.HTTP_200_OK,
            "file_id": result["$id"],
            "preview_url": str(preview_img),
            "message": "Profile image uploaded and updated successfully",
        }

    except AppwriteException as e:
        logger.error(f"Appwrite Error: {e.message}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Appwrite error: {e.message}")
    except Exception as e:
        logger.error(f"Server Error: {e.message}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.delete(
    "/delete-profile-image",
    status_code=status.HTTP_200_OK,
)
async def delete_profile_image(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)

    image_id = await repo.get_image_id(current_user.id)

    if not image_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not have a profile image to delete.",
        )

    try:
        appwrite_client = AppwriteClient()
        appwrite_client.delete_upload(file_id=image_id)

        await repo.update_profile_image(current_user.id, "")

    except AppwriteException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An Appwrite error occurred: {e.message}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )

    return {
        "version": "v1",
        "status": "success",
        "message": "Profile image deleted successfully.",
    }
