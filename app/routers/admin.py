from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.auth.dependencies import get_current_admin_user
from app.models import User

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=list[dict])
async def get_all_users(
    admin_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "is_admin": user.is_admin
        } for user in users
    ]
