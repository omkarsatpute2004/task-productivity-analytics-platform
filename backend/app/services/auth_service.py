from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.core import security


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, req: RegisterRequest) -> UserResponse:
        existing = self.user_repo.get_by_email(req.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email address already exists."
            )

        hashed_password = security.get_password_hash(req.password)
        user = User(
            name=req.name,
            email=req.email,
            password_hash=hashed_password,
            role=UserRole.USER,
            department=req.department
        )
        created_user = self.user_repo.create(user)
        return UserResponse.model_validate(created_user)

    def login(self, req: LoginRequest) -> TokenResponse:
        user = self.user_repo.get_by_email(req.email)
        if not user or not security.verify_password(req.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials.",
                headers={"WWW-Authenticate": "Bearer"}
            )

        access_token = security.create_access_token(subject=user.id)
        user_response = UserResponse.model_validate(user)
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
