from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

from app.database import get_db
from app import models
from app.services.redis_cache import get_cached_user, set_cached_user

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Check Redis cache
    cached_user = await get_cached_user(email)
    if cached_user:
        return models.User(**cached_user)  # ⬅️ Повертаємо ORM-сумісний об'єкт

    # DB fallback
    result = await db.execute(select(models.User).filter_by(email=email))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    await set_cached_user(email, {
        "id": user.id,
        "email": user.email,
        "is_verified": user.is_verified,
        "avatar_url": user.avatar_url,
        "is_admin": user.is_admin
    })
    return user


async def get_current_admin_user(
    current_user: models.User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
