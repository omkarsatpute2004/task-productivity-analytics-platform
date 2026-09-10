from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", status_code=status.HTTP_200_OK)
def check_health():
    """Service health check endpoint."""
    return {
        "status": "ok",
        "service": "task-productivity-platform"
    }


@router.get("/db", status_code=status.HTTP_200_OK)
def check_db_health(db: Session = Depends(get_db)):
    """Database connectivity health check endpoint."""
    try:
        result = db.execute(text("SELECT 1")).scalar()
        if result == 1:
            return {
                "status": "ok",
                "database": "ok",
                "service": "task-productivity-platform"
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database query returned unexpected result"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {str(e)}"
        )
