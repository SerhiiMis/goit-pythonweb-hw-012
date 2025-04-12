import os
import time
import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from asgi_lifespan import LifespanManager

from app import database, models
from app.database import Base, get_db

# Створюємо тестовий engine ДО імпорту app
DATABASE_URL_TEST = "sqlite+aiosqlite:///./test_temp.db"
test_engine = create_async_engine(DATABASE_URL_TEST, echo=False, future=True)
TestingSessionLocal = sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)

# Заміна engine та get_db ДО імпорту FastAPI app
database.engine = test_engine

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

# І тільки зараз імпортуємо app
from app.main import app
app.dependency_overrides[get_db] = override_get_db


# @pytest.mark.asyncio
# async def test_signup_and_login_and_user_profile():
#     async with LifespanManager(app):
#         # Створюємо таблиці після старту Lifespan
#         async with test_engine.begin() as conn:
#             await conn.run_sync(Base.metadata.create_all)

#         transport = ASGITransport(app=app)
#         async with AsyncClient(transport=transport, base_url="http://test") as ac:
#             signup_payload = {"email": "integration@example.com", "password": "secret"}
#             signup_response = await ac.post("/auth/signup", json=signup_payload)
#             assert signup_response.status_code == 201

#             login_payload = {"username": "integration@example.com", "password": "secret"}
#             login_response = await ac.post("/auth/login", data=login_payload)
#             assert login_response.status_code == 200
#             token = login_response.json()["access_token"]

#             headers = {"Authorization": f"Bearer {token}"}
#             profile_response = await ac.get("/users/me", headers=headers)
#             assert profile_response.status_code == 200
#             assert profile_response.json()["email"] == "integration@example.com"


@pytest.fixture(scope="session", autouse=True)
def cleanup_db():
    yield
    asyncio.run(test_engine.dispose())
    time.sleep(0.2)
    if os.path.exists("test_temp.db"):
        os.remove("test_temp.db")
