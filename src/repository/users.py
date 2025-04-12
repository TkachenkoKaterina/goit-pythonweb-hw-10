from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.entity.models import User
from src.schemas.user import UserCreate
from src.services.hash import get_password_hash


async def get_user_by_email(email: str, db: AsyncSession) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_user(user_data: UserCreate, db: AsyncSession) -> User:
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password=hashed_password
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def verify_user(user: User, db: AsyncSession) -> User:
    user.is_verified = True
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_avatar(email: str, avatar_url: str, db: AsyncSession) -> User:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        user.avatar = avatar_url
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user
