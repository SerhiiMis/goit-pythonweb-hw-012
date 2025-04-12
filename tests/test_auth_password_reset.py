import sys
import os
import pytest
from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from httpx import AsyncClient, ASGITransport

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app import schemas, crud
from app.auth.security import create_access_token
from app.database import get_db

@pytest.mark.asyncio
async def test_password_reset_flow(test_db: AsyncSession):
    # Очищення таблиці користувачів перед тестом
    await test_db.execute(text("DELETE FROM users"))
    await test_db.commit()

    # Переоприділення залежності на тестову БД
    app.dependency_overrides[get_db] = lambda: test_db

    test_email = "resetuser@example.com"
    old_password = "oldpassword"
    new_password = "newsecurepass"

    # Створення і верифікація користувача
    user_data = schemas.UserCreate(email=test_email, password=old_password)
    user = await crud.create_user(user_data, test_db)
    user.is_verified = True
    await test_db.commit()

    # HTTP-клієнт з ASGI транспортом (без сервера!)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:

        # Запит на скидання пароля
        response = await ac.post("/auth/request-password-reset", json={"email": test_email})
        assert response.status_code == 200
        assert response.json()["message"] == "Password reset link has been sent"

        # Генерація токена вручну (імітація email-посилання)
        token = create_access_token({"sub": test_email, "type": "reset"}, expires_delta=timedelta(minutes=30))

        # Скидання пароля
        response = await ac.post("/auth/reset-password", json={"token": token, "new_password": new_password})
        assert response.status_code == 200
        assert response.json()["message"] == "Password has been reset successfully"

        # Перевірка логіну з новим паролем
        response = await ac.post("/auth/login", json={"email": test_email, "password": new_password})
        assert response.status_code == 200
        assert "access_token" in response.json()
