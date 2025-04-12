import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import asyncio
from datetime import datetime, timedelta

# Import necessary components from SQLAlchemy for creating an in-memory test database
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import our CRUD functions, models, and Pydantic schemas from the app
from app import crud, models, schemas
from app.database import Base

# Define the in-memory database URL using SQLite and aiosqlite driver
DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """
    Provide an event loop for the entire test session.
    This fixture ensures that all async tests use the same loop.
    """
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

import pytest_asyncio

@pytest_asyncio.fixture
async def test_db():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    # Create the tables in the test database.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session = async_session()
    try:
        yield session
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_create_user(test_db):
    """
    Test that the create_user function successfully creates a new user with a hashed password.
    """
    user_data = schemas.UserCreate(email="test@example.com", password="secret")
    user = await crud.create_user(user_data, test_db)
    
    # Verify the returned user has a valid ID and the correct email
    assert user.id is not None, "User ID should not be None after creation."
    assert user.email == "test@example.com", "User email does not match the provided email."

@pytest.mark.asyncio
async def test_get_user_by_email(test_db):
    """
    Test that get_user_by_email returns the correct user after creation.
    """
    user_data = schemas.UserCreate(email="findme@example.com", password="secret")
    await crud.create_user(user_data, test_db)
    
    user = await crud.get_user_by_email("findme@example.com", test_db)
    assert user is not None, "User should be found by email."
    assert user.email == "findme@example.com", "Retrieved user's email is incorrect."

@pytest.mark.asyncio
async def test_update_contact(test_db):
    """
    Test updating a contact:
      - Create a user and a contact.
      - Update the contact's first name.
      - Verify the update was successful.
    """
    # Create a user
    user_data = schemas.UserCreate(email="update@example.com", password="secret")
    user = await crud.create_user(user_data, test_db)
    
    # Create a contact for the user
    contact_create = schemas.ContactCreate(
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
        phone="+123456789",
        birthday="1990-05-01",
        extra_info="Friend"
    )
    contact = await crud.create_contact(contact_create, test_db, user)
    
    # Prepare update: change the first name
    update_data = schemas.ContactUpdate(first_name="Alicia")
    updated_contact = await crud.update_contact(contact.id, update_data, test_db, user)
    
    assert updated_contact.first_name == "Alicia", "Contact first name was not updated."

@pytest.mark.asyncio
async def test_delete_contact(test_db):
    """
    Test deleting a contact:
      - Create a user and a contact.
      - Delete the contact.
      - Verify that the contact is no longer found.
    """
    user_data = schemas.UserCreate(email="delete@example.com", password="secret")
    user = await crud.create_user(user_data, test_db)

    contact_create = schemas.ContactCreate(
        first_name="Bob",
        last_name="Brown",
        email="bob@example.com",
        phone="+987654321",
        birthday="1985-08-15",
        extra_info="Colleague"
    )
    contact = await crud.create_contact(contact_create, test_db, user)
    
    deletion_result = await crud.delete_contact(contact.id, test_db, user)
    assert deletion_result, "Contact deletion should return True."

    # Attempt to retrieve the deleted contact
    deleted_contact = await crud.get_contact(contact.id, test_db, user)
    assert deleted_contact is None, "Deleted contact should not be found."

@pytest.mark.asyncio
async def test_search_contacts(test_db):
    """
    Test the search_contacts function:
      - Create a user and multiple contacts.
      - Search for contacts using a query term.
      - Verify that the search returns the expected results.
    """
    user_data = schemas.UserCreate(email="search@example.com", password="secret")
    user = await crud.create_user(user_data, test_db)

    contact1 = schemas.ContactCreate(
        first_name="Charlie",
        last_name="Daniels",
        email="charlie@example.com",
        phone="+111111111",
        birthday="1992-03-10",
        extra_info="Friend"
    )
    contact2 = schemas.ContactCreate(
        first_name="Charlotte",
        last_name="Jones",
        email="charlotte@example.com",
        phone="+222222222",
        birthday="1993-04-20",
        extra_info="Colleague"
    )
    await crud.create_contact(contact1, test_db, user)
    await crud.create_contact(contact2, test_db, user)
    
    results = await crud.search_contacts("Charl", test_db, user)
    assert len(results) >= 2, "Search should find at least two contacts with 'Charl'."

@pytest.mark.asyncio
async def test_upcoming_birthdays(test_db):
    """
    Test the upcoming_birthdays function:
      - Create a user and a contact with a birthday within the next 7 days.
      - Verify that the function returns at least one contact.
    """
    user_data = schemas.UserCreate(email="birthday@example.com", password="secret")
    user = await crud.create_user(user_data, test_db)

    today = datetime.today().date()
    # Set birthday 3 days from now
    birthday = (today + timedelta(days=3)).isoformat()

    contact_create = schemas.ContactCreate(
        first_name="Diana",
        last_name="Prince",
        email="diana@example.com",
        phone="+333333333",
        birthday=birthday,
        extra_info="Superhero"
    )
    await crud.create_contact(contact_create, test_db, user)
    
    upcoming = await crud.upcoming_birthdays(test_db, user)
    assert len(upcoming) > 0, "There should be at least one contact with an upcoming birthday."
