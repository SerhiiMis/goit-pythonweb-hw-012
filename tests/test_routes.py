import os
os.environ["SECRET_KEY"] = "supersecretkey"

import pytest
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager  # Новий імпорт
from app.main import app


@pytest.mark.asyncio
async def test_signup_and_login_and_user_profile():
    """
    Integration test covering:
      - User registration (/auth/signup)
      - Email verification (/auth/verify-email)
      - User login (/auth/login)
      - Access to the protected endpoint (/users/me)
    """
    # Обгортаємо застосунок у LifespanManager, щоб запустився startup (створення таблиць)
    async with LifespanManager(app):
        # Також використовуємо ASGITransport для клієнта
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            # --- SIGNUP ---
            signup_payload = {"email": "integration@example.com", "password": "secret"}
            signup_response = await ac.post("/auth/signup", json=signup_payload)
            assert signup_response.status_code == 201, f"Signup failed: {signup_response.text}"
            signup_data = signup_response.json()
            assert signup_data["email"] == "integration@example.com"

            # --- VERIFY EMAIL ---
            verify_response = await ac.get("/auth/verify-email", params={"email": "integration@example.com"})
            assert verify_response.status_code == 200, f"Email verification failed: {verify_response.text}"
            verify_data = verify_response.json()
            assert verify_data["message"] == "Email verified successfully"

            # --- LOGIN ---
            login_payload = {"email": "integration@example.com", "password": "secret"}
            login_response = await ac.post("/auth/login", json=login_payload)
            assert login_response.status_code == 200, f"Login failed: {login_response.text}"
            login_data = login_response.json()
            assert "access_token" in login_data, "Login did not return access_token"
            token = login_data["access_token"]

            # --- ACCESS PROTECTED ROUTE (/users/me) ---
            headers = {"Authorization": f"Bearer {token}"}
            user_response = await ac.get("/users/me", headers=headers)
            assert user_response.status_code == 200, f"Accessing /users/me failed: {user_response.text}"
            user_data = user_response.json()
            assert user_data["email"] == "integration@example.com", "Returned user email does not match signup email"
