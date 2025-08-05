from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.logger import get_logger
from app.repository.user import UserRepository
from app.config.database import get_db
from app.schema.user_schema import UserRegister, Token, ProfileResponse, UploadProfile
from app.authentication.models import User
from app.authentication.jwt.token import create_access_token
from app.authentication.jwt.oauth2 import get_current_user
import traceback
import os
import uuid
import shutil
from appwrite.input_file import InputFile
from appwrite.exception import AppwriteException
from app.config.appwrite_client import AppwriteClient
from appwrite.query import Query
from appwrite.id import ID # Import ID
from appwrite.permission import Permission # Import Permission
from appwrite.role import Role # Import Role
from app.config.conf import appwrite_endpoint, appwrite_projectId, appwrite_bucketId

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
                detail="User already exists in the system"
            )

        await repo.create_user(data.email, data.password)
        logger.info("User registered successfully.")

        return {
            "version": "v1",
            "status": status.HTTP_200_OK,
            "message": "User has been registered successfully"
        }

    except HTTPException:
        # re-raise HTTPException as-is to keep correct status code
        raise

    except Exception as e:
        logger.error(f"Signup Error: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
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
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        access_token = create_access_token(user_id=user.id)
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Login Error: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.get("/me", response_model=ProfileResponse)
async def me(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    repo = UserRepository(db)
    user = await repo.profile_details(current_user.id)
    
    return {
        "version":"v1",
        "status": status.HTTP_200_OK,
        "id": user.id,
        "email": user.email,
        "profile_img": user.profile_img,
        "is_oauth": user.is_oauth,
        "uploaded_links": user.uploaded_links,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
    }

## TODO: Migrate app write logic to the utils 
@router.post("/upload-profile-image/", response_model=UploadProfile)
async def upload_profile_image(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    temp_filename = f"/tmp/{uuid.uuid4()}_{file.filename}"
    try:
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        appwrite_action = AppwriteClient()
        storage = appwrite_action.get_storage()

        # Corrected create_file call
        result = storage.create_file(
            bucket_id=appwrite_bucketId,
            file_id=ID.unique(), # Use ID.unique() for generating unique IDs
            file=InputFile.from_path(temp_filename),
            permissions=[
                Permission.read(Role.any()),  # Allows anyone to read
                Permission.write(Role.user(current_user.id)) # Allows only the current user to write
            ]
        )

        os.remove(temp_filename)

        # Note: bucket_id for get_file_preview should match the one used for create_file
        # which is "profile-images", not "profile-img" as in your original code.
        ## -> As i donot have premimum of appwrite so unable to use this feature
        # preview_url = storage.get_file_preview(
        #     bucket_id=appwrite_bucketId,
        #     file_id=result["$id"]
        # )

        # Work arounds
        APPWRITE_ENDPOINT = appwrite_endpoint 
        APPWRITE_PROJECT_ID = appwrite_projectId

        final_file_url = (
            f"{APPWRITE_ENDPOINT}/storage/buckets/{result['bucketId']}/files/{result['$id']}/view?project={APPWRITE_PROJECT_ID}&mode=admin"
        )


        repo = UserRepository(db)
        updated_user = await repo.update_profile_image(current_user.id, str(final_file_url))
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found or update failed")

        return {
            "version": "v1",
            "status": status.HTTP_200_OK,
            "file_id": result["$id"],
            "preview_url": str(final_file_url),
            "message": "Profile image uploaded and updated successfully"
        }

    except AppwriteException as e:
        logger.error(f"Appwrite error: {e.message}")
        raise HTTPException(status_code=500, detail=f"Appwrite error: {e.message}")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

