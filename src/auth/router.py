from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from src.database.db import get_db
from src.repository import users as repo_users
from src.schemas.user import UserCreate, UserResponse, Token
from src.services.auth import (
    create_access_token,
    create_email_token,
    decode_email_token,
)
from src.services.hash import verify_password
from src.services.email import send_verification_email
from src.entity.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def signup(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    existing = await repo_users.get_user_by_email(user_data.email, db)
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")

    user = await repo_users.create_user(user_data, db)

    token = create_email_token({"sub": user.email})
    await send_verification_email(user.email, token)

    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user: User = await repo_users.get_user_by_email(form_data.username, db)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/verify/{token}")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    email = decode_email_token(token)
    if email is None:
        raise HTTPException(
            status_code=400, detail="Invalid verification token"
        )

    user = await repo_users.get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.is_verified:
        return {"message": "Email already verified"}

    await repo_users.verify_user(user, db)
    return {"message": "Email successfully verified"}
