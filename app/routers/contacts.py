from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .. import crud, schemas
from ..database import get_db
from ..auth.dependencies import get_current_user
from ..models import User

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.post("/", response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(contact: schemas.ContactCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await crud.create_contact(contact, db, current_user)


@router.get("/", response_model=List[schemas.ContactResponse])
async def get_contacts(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await crud.get_contacts(db, current_user)


@router.get("/{contact_id}", response_model=schemas.ContactResponse)
async def get_contact(contact_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    contact = await crud.get_contact(contact_id, db, current_user)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=schemas.ContactResponse)
async def update_contact(contact_id: int, updated: schemas.ContactUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    contact = await crud.update_contact(contact_id, updated, db, current_user)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    deleted = await crud.delete_contact(contact_id, db, current_user)
    if not deleted:
        raise HTTPException(status_code=404, detail="Contact not found")


@router.get("/search/", response_model=List[schemas.ContactResponse])
async def search_contacts(query: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await crud.search_contacts(query, db, current_user)


@router.get("/upcoming-birthdays/", response_model=List[schemas.ContactResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await crud.upcoming_birthdays(db, current_user)
