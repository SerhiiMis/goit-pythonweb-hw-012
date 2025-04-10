from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

from fastapi.security import OAuth2PasswordBearer

from app.routers import contacts, auth, users
from app.services.limiter import limiter
from app import database

app = FastAPI(title="Contacts API", debug=True)

# Init rate limiter
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# OAuth2 config for Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@app.get("/token-test")
async def token_test(token: str = Depends(oauth2_scheme)):
    return {"token": token}

# Add Authorize button to Swagger
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Contacts API",
        version="1.0.0",
        description="API for managing contacts with JWT authentication",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", []).append({"BearerAuth": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Rate limit error handler
@app.exception_handler(RateLimitExceeded)
async def ratelimit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded. Try again later."}
    )

# Routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(contacts.router)

# DB init
@app.on_event("startup")
async def on_startup():
    async with database.engine.begin() as conn:
        await conn.run_sync(database.Base.metadata.create_all)

app.openapi = custom_openapi