from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import date, timedelta
from src.entity.models import Contact
from src.schemas.contact import ContactCreate, ContactUpdate


async def get_contacts(skip: int, limit: int, db: AsyncSession):
    stmt = select(Contact).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession):
    stmt = select(Contact).where(Contact.id == contact_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_contact(contact: ContactCreate, db: AsyncSession):
    new_contact = Contact(**contact.dict())
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    return new_contact


async def update_contact(
    contact_id: int, contact: ContactUpdate, db: AsyncSession
):
    db_contact = await get_contact(contact_id, db)
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        await db.commit()
        await db.refresh(db_contact)
    return db_contact


async def delete_contact(contact_id: int, db: AsyncSession):
    db_contact = await get_contact(contact_id, db)
    if db_contact:
        await db.delete(db_contact)
        await db.commit()
    return db_contact


async def search_contacts(query: str, db: AsyncSession):
    stmt = select(Contact).where(
        or_(
            Contact.first_name.ilike(f"%{query}%"),
            Contact.last_name.ilike(f"%{query}%"),
            Contact.email.ilike(f"%{query}%"),
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_birthdays_next_week(db: AsyncSession):
    today = date.today()
    next_week = today + timedelta(days=7)
    stmt = select(Contact).where(Contact.birthday.between(today, next_week))
    result = await db.execute(stmt)
    return result.scalars().all()
