"""Auth routes — register and login."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...infrastructure.database import get_db, UserModel
from ...infrastructure.auth import hash_password, verify_password, create_token
from ..schemas import UserRegister, UserLogin, TokenResponse

logger = logging.getLogger("xborder")
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    existing = await db.execute(select(UserModel).where(UserModel.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = UserModel(
        email=data.email,
        password_hash=hash_password(data.password),
        name=data.name,
        company=data.company,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_token(str(user.id))
    logger.info(f"User registered: {user.email}")
    return TokenResponse(access_token=token, user_id=str(user.id), email=user.email)


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login and get JWT token."""
    result = await db.execute(select(UserModel).where(UserModel.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(str(user.id))
    logger.info(f"User logged in: {user.email}")
    return TokenResponse(access_token=token, user_id=str(user.id), email=user.email)
