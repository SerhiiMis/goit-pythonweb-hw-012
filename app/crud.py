from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_, extract
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from fastapi import HTTPException, status

from . import models, schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def get_user_by_email(email: str, db: AsyncSession) -> Optional[models.User]:
    """
    Retrieve a user by email from the database.

    :param email: The email address of the user.
    :param db: The asynchronous database session.
    :return: The user instance if found, otherwise None.
    """
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalar_one_or_none()


async def create_user(user_data: schemas.UserCreate, db: AsyncSession) -> models.User:
    """
    Create a new user with a hashed password.

    :param user_data: Schema containing user's email and password.
    :param db: The asynchronous database session.
    :return: The newly created user object.
    :raises HTTPException: If a user with the same email already exists.
    """
    result = await db.execute(select(models.User).where(models.User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists."
        )

    hashed_password = pwd_context.hash(user_data.password)
    new_user = models.User(
        email=user_data.email,
        password=hashed_password,
        is_admin=True
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


# === CONTACT CRUD ===

async def create_contact(contact: schemas.ContactCreate, db: AsyncSession, user: models.User) -> models.Contact:
    """
    Create a new contact for the given user.

    :param contact: Schema containing the contact's data.
    :param db: The asynchronous database session.
    :param user: The owner user of the contact.
    :return: The newly created contact object.
    """
    new_contact = models.Contact(**contact.dict(), owner_id=user.id)
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)
    return new_contact


async def get_contact(contact_id: int, db: AsyncSession, user: models.User) -> Optional[models.Contact]:
    """
    Retrieve a contact by its ID for a specific user.

    :param contact_id: The unique identifier of the contact.
    :param db: The asynchronous database session.
    :param user: The owner user of the contact.
    :return: The contact object if found, otherwise None.
    """
    result = await db.execute(
        select(models.Contact).where(models.Contact.id == contact_id, models.Contact.owner_id == user.id)
    )
    return result.scalar_one_or_none()


async def get_contacts(db: AsyncSession, user: models.User) -> List[models.Contact]:
    """
    Retrieve all contacts for a given user.

    :param db: The asynchronous database session.
    :param user: The owner user.
    :return: A list of contacts belonging to the user.
    """
    result = await db.execute(select(models.Contact).where(models.Contact.owner_id == user.id))
    return result.scalars().all()


async def update_contact(contact_id: int, updated: schemas.ContactUpdate, db: AsyncSession, user: models.User) -> Optional[models.Contact]:
    """
    Update details of an existing contact.

    :param contact_id: The unique identifier of the contact.
    :param updated: Schema containing fields to update.
    :param db: The asynchronous database session.
    :param user: The owner user.
    :return: The updated contact object if found, otherwise None.
    """
    contact = await get_contact(contact_id, db, user)
    if contact:
        for field, value in updated.dict(exclude_unset=True).items():
            setattr(contact, field, value)
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: models.User) -> bool:
    """
    Delete a specific contact for a user.

    :param contact_id: The unique identifier of the contact.
    :param db: The asynchronous database session.
    :param user: The owner user.
    :return: True if deletion was successful, False otherwise.
    """
    contact = await get_contact(contact_id, db, user)
    if contact:
        await db.delete(contact)
        await db.commit()
        return True
    return False


async def search_contacts(query: str, db: AsyncSession, user: models.User) -> List[models.Contact]:
    """
    Search for contacts by first name, last name, or email.

    :param query: The search string.
    :param db: The asynchronous database session.
    :param user: The owner user.
    :return: A list of contacts matching the query.
    """
    result = await db.execute(
        select(models.Contact).where(
            models.Contact.owner_id == user.id,
            or_(
                models.Contact.first_name.ilike(f"%{query}%"),
                models.Contact.last_name.ilike(f"%{query}%"),
                models.Contact.email.ilike(f"%{query}%")
            )
        )
    )
    return result.scalars().all()


async def upcoming_birthdays(db: AsyncSession, user: models.User) -> List[models.Contact]:
    """
    Retrieve contacts with birthdays in the next 7 days for a specific user.

    :param db: The asynchronous database session.
    :param user: The owner user.
    :return: A list of contacts with upcoming birthdays.
    """
    today = datetime.today().date()
    in_seven_days = today + timedelta(days=7)

    result = await db.execute(
        select(models.Contact).where(
            models.Contact.owner_id == user.id,
            extract('month', models.Contact.birthday) == today.month,
            extract('day', models.Contact.birthday) >= today.day,
            extract('day', models.Contact.birthday) <= in_seven_days.day
        )
    )
    return result.scalars().all()
