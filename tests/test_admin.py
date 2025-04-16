import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.database import get_db
from app.schemas import UserCreate
from app.auth.security import create_access_token
from app import crud


@pytest.mark.asyncio
async def test_get_users_as_admin(test_db: AsyncSession):
    # Override the default database dependency with the test session
    app.dependency_overrides[get_db] = lambda: test_db

    # Create an admin user
    admin_data = UserCreate(email="admin@example.com", password="adminpass")
    admin = await crud.create_user(admin_data, test_db, is_admin=True)

    # Mark the user as verified (if required for login)
    admin.is_verified = True
    await test_db.commit()

    # Generate JWT access token for the admin
    token = create_access_token({"sub": admin.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Make a GET request to the /admin/users route
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/admin/users", headers=headers)

    # Assert the response is successful and contains the admin
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(user["email"] == "admin@example.com" for user in data)
