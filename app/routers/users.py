from fastapi import APIRouter, Depends, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.limiter import limiter
from app.services.cloudinary_service import upload_avatar
from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models import User
from app import schemas

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
@limiter.limit("5/minute")
async def get_me(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_verified": current_user.is_verified,
        "avatar_url": current_user.avatar_url,
    }


@router.post("/avatar", response_model=schemas.UserResponse)
async def update_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    public_id = f"user_{current_user.id}_avatar"
    avatar_url = upload_avatar(file.file, public_id)
    current_user.avatar_url = avatar_url
    await db.commit()
    await db.refresh(current_user)
    return current_user
