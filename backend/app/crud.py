import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    BusinessUnit,
    BusinessUnitCreate,
    BusinessUnitUpdate,
    File,
    FileCreate,
    FileFunctionLink,
    Function,
    FunctionCreate,
    FunctionUpdate,
    Item,
    ItemCreate,
    User,
    UserCreate,
    UserUpdate,
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


# Dummy hash to use for timing attack prevention when user is not found
# This is an Argon2 hash of a random password, used to ensure constant-time comparison
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        # Prevent timing attacks by running password verification even when user doesn't exist
        # This ensures the response time is similar whether or not the email exists
        verify_password(password, DUMMY_HASH)
        return None
    verified, updated_password_hash = verify_password(password, db_user.hashed_password)
    if not verified:
        return None
    if updated_password_hash:
        db_user.hashed_password = updated_password_hash
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def create_file(*, session: Session, file_in: FileCreate, owner_id: uuid.UUID) -> File:
    db_file = File.model_validate(file_in, update={"owner_id": owner_id})
    session.add(db_file)
    session.commit()
    session.refresh(db_file)
    return db_file


def get_file_by_id(*, session: Session, file_id: uuid.UUID) -> File | None:
    statement = select(File).where(File.id == file_id)
    session_file = session.exec(statement).first()
    return session_file


def get_files_by_owner(
    *, session: Session, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[File]:
    statement = select(File).where(File.owner_id == owner_id).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_files_count_by_owner(*, session: Session, owner_id: uuid.UUID) -> int:
    statement = select(File).where(File.owner_id == owner_id)
    return len(session.exec(statement).all())


def delete_file(*, session: Session, db_file: File) -> File:
    session.delete(db_file)
    session.commit()
    return db_file


# =============================================================================
# BusinessUnit CRUD
# =============================================================================


def create_business_unit(*, session: Session, bu_in: BusinessUnitCreate) -> BusinessUnit:
    db_obj = BusinessUnit.model_validate(bu_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_business_unit_by_id(*, session: Session, bu_id: uuid.UUID) -> BusinessUnit | None:
    return session.get(BusinessUnit, bu_id)


def get_business_units(
    *, session: Session, skip: int = 0, limit: int = 100
) -> list[BusinessUnit]:
    statement = select(BusinessUnit).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_business_unit(
    *, session: Session, db_bu: BusinessUnit, bu_in: BusinessUnitUpdate
) -> BusinessUnit:
    bu_data = bu_in.model_dump(exclude_unset=True)
    db_bu.sqlmodel_update(bu_data)
    session.add(db_bu)
    session.commit()
    session.refresh(db_bu)
    return db_bu


def delete_business_unit(*, session: Session, db_bu: BusinessUnit) -> BusinessUnit:
    session.delete(db_bu)
    session.commit()
    return db_bu


# =============================================================================
# Function CRUD
# =============================================================================


def create_function(*, session: Session, func_in: FunctionCreate) -> Function:
    db_obj = Function.model_validate(func_in)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_function_by_id(*, session: Session, func_id: uuid.UUID) -> Function | None:
    return session.get(Function, func_id)


def get_functions_by_bu(
    *, session: Session, bu_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> list[Function]:
    statement = select(Function).where(Function.business_unit_id == bu_id).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def get_functions(
    *, session: Session, skip: int = 0, limit: int = 100
) -> list[Function]:
    statement = select(Function).offset(skip).limit(limit)
    return list(session.exec(statement).all())


def update_function(
    *, session: Session, db_func: Function, func_in: FunctionUpdate
) -> Function:
    func_data = func_in.model_dump(exclude_unset=True)
    db_func.sqlmodel_update(func_data)
    session.add(db_func)
    session.commit()
    session.refresh(db_func)
    return db_func


def delete_function(*, session: Session, db_func: Function) -> Function:
    session.delete(db_func)
    session.commit()
    return db_func


# =============================================================================
# File Permission Checking
# =============================================================================


def check_file_access(*, session: Session, file: File, user: User) -> bool:
    """
    Check if user has access to file based on:
    1. User is superuser
    2. User is file owner
    3. File's visible_bu matches user's business_unit
    4. File's visible_functions includes user's function
    5. No restrictions set (file is public to all authenticated users)
    """
    if user.is_superuser:
        return True
    if file.owner_id == user.id:
        return True

    # If no restrictions, allow access
    if not file.visible_bu_id and not file.visible_functions:
        return True

    # Check BU visibility
    if file.visible_bu_id and user.business_unit_id == file.visible_bu_id:
        return True

    # Check Function visibility
    if file.visible_functions and user.function_id:
        file_function_ids = [f.id for f in file.visible_functions]
        if user.function_id in file_function_ids:
            return True

    return False
