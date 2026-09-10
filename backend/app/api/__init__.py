from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.categories import router as categories_router
from app.api.tasks import router as tasks_router
from app.api.analytics import router as analytics_router
from app.api.ml import router as ml_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(categories_router)
api_router.include_router(tasks_router)
api_router.include_router(analytics_router)
api_router.include_router(ml_router)


