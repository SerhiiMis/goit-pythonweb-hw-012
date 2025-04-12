from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from .. import schemas, crud
from ..database import get_db
from ..auth.security import verify_password, create_access_token
from ..services import email as email_service
from ..services.cloudinary_service import upload_avatar
from ..auth.dependencies import get_current_user
from ..models import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: schemas.UserCreate, request: Request, db: AsyncSession = Depends(get_db)):
    """
    Register a new user and send an email verification link.

    :param user_data: Schema containing the user's email and password.
    :param request: Request object to generate verification link.
    :param db: The asynchronous database session.
    :return: The created user object.
    """
    user = await crud.create_user(user_data, db)
    email_service.send_verification_email(request, user.email)
    return user

@router.get("/verify-email")
async def verify_email(email: str, db: AsyncSession = Depends(get_db)):
    """
    Verify a user's email address.

    Updates the user's verification status to True if a user with the provided email exists.

    :param email: The email address to verify.
    :param db: The asynchronous database session.
    :return: A message confirming successful verification.
    :raises HTTPException: If the user is not found.
    """
    user = await crud.get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    await db.commit()
    return {"message": "Email verified successfully"}

@router.post("/login")
async def login(user: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Authenticate a user and issue a JWT token.

    :param user: Schema containing login credentials (email and password).
    :param db: The asynchronous database session.
    :return: A dictionary with the access token and token type.
    :raises HTTPException: If authentication fails.
    """
    db_user = await crud.get_user_by_email(user.email, db)
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(data={"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}
