from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    HTTPException,
    status,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession
import cloudinary.uploader

from src.database.db import get_db
from src.schemas.user import UserResponse
from src.services.auth import get_current_user
from src.repository import users as repo_users
from src.entity.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return current_user


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported file type. Please upload JPEG, PNG, or "
                "WEBP images."
            ),
        )

    try:
        public_id = f"phonebook_avatars/{current_user.username}"
        upload_result = cloudinary.uploader.upload(
            file.file,
            public_id=public_id,
            overwrite=True,
            folder="phonebook_avatars",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cloudinary upload failed: {e}",
        )

    avatar_url = upload_result.get("secure_url")
    await repo_users.update_avatar(current_user.email, avatar_url, db)
    return {"avatar_url": avatar_url}
