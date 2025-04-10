# Contacts API

A secure asynchronous REST API for managing personal contacts, built with FastAPI, PostgreSQL, JWT and Docker.

## Features

- JWT-based authentication and authorization
- Only authenticated users can access their own contacts
- Email verification via link
- Rate limiting for the `/users/me` endpoint
- CORS enabled for API
- Avatar upload with Cloudinary integration
- Docker Compose support for quick startup

## Technologies

- Python 3.12+
- FastAPI
- SQLAlchemy (Async)
- PostgreSQL + asyncpg
- Alembic
- Docker & Docker Compose
- Pydantic v2
- Uvicorn
- python-jose (JWT)
- Cloudinary SDK
- SlowAPI (rate limit)

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/SerhiiMis/goit-pythonweb-hw-10.git
cd goit-pythonweb-hw-10
```

### 2. Create and configure `.env`

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/contacts_db
SECRET_KEY=your_secret_key

CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### 3. Run with Docker

```bash
docker compose up --build
```

App will be available at:  
📄 Swagger UI → [http://localhost:8000/docs](http://localhost:8000/docs)

## API Overview

### 🔐 Authentication

- `POST /auth/signup` — Register user
- `POST /auth/login` — Login and receive JWT
- `GET /auth/verify-email?email=...` — Verify user email

### 👤 Users

- `GET /users/me` — Get current user info (rate-limited)
- `POST /users/avatar` — Upload user avatar to Cloudinary

### 📇 Contacts (authorized access only)

- `POST /contacts/` — Create new contact
- `GET /contacts/` — Get all user's contacts
- `GET /contacts/{id}` — Get contact by ID
- `PUT /contacts/{id}` — Update contact
- `DELETE /contacts/{id}` — Delete contact
- `GET /contacts/search/?query=...` — Search contacts
- `GET /contacts/upcoming-birthdays/` — Birthdays in next 7 days

## Environment Files

- `.env` — used for environment variables (not committed)
- `.example.env` — shows required env variables
- `docker-compose.yml` — builds API and DB containers
