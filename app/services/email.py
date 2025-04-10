from fastapi import Request
from urllib.parse import urlencode


def generate_verification_link(request: Request, email: str) -> str:
    """
    Generates a verification link based on the request's base URL and user's email.
    """
    base_url = str(request.base_url)  # e.g., http://127.0.0.1:8000/
    token = email  # Для реалізації, токен — це email
    query = urlencode({"token": token})
    return f"{base_url}auth/verify-email?{query}"


def send_verification_email(request: Request, email: str) -> None:
    """
    Logs the verification link to the console (you can replace this with real email sending).
    """
    verification_link = generate_verification_link(request, email)
    print(f"📧 Email verification link for {email}: {verification_link}")
