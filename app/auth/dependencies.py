from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

from ..database import get_db
from .. import models
from ..services.redis_cache import get_cached_user, set_cached_user
from ..schemas import UserResponse

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> models.User:
    """
    Retrieves the current user either from Redis cache or from the database.
    Decodes the JWT token to extract the user's email.
    Caches the user data on first retrieval from the DB.
    """
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

    # Check Redis cache for user data
    cached_user = await get_cached_user(email)
    if cached_user:
        # Return a Pydantic model (UserResponse) created from cached dict,
        # which allows attribute access similar to an ORM model.
        return UserResponse(**cached_user)

    # If not in cache, fetch from database
    result = await db.execute(select(models.User).filter_by(email=email))
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    # Cache the user data (using the Pydantic model to serialize)
    user_data = UserResponse.from_orm(user).dict()
    await set_cached_user(email, user_data)
    return user
