from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api import api_router

app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API foundation for Task Management & Productivity Analytics Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

app.include_router(api_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to avoid exposing internal stack traces in production."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."}
    )
