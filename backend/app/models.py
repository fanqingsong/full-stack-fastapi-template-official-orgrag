import uuid
from datetime import datetime, timezone

from pydantic import EmailStr
from sqlalchemy import DateTime
from sqlmodel import Field, Relationship, SQLModel


def get_datetime_utc() -> datetime:
    return datetime.now(timezone.utc)


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    business_unit_id: uuid.UUID | None = Field(default=None, foreign_key="businessunit.id")
    function_id: uuid.UUID | None = Field(default=None, foreign_key="function.id")


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    files: list["File"] = Relationship(back_populates="owner", cascade_delete=True)
    business_unit: "BusinessUnit" = Relationship(back_populates="users")
    function: "Function" = Relationship(back_populates="users")


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


# =============================================================================
# Organization Models - Must be defined before File
# =============================================================================

# BusinessUnit models
class BusinessUnitBase(SQLModel):
    name: str = Field(max_length=255, unique=True, index=True)
    code: str = Field(max_length=50, unique=True)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool = True


class BusinessUnitCreate(BusinessUnitBase):
    pass


class BusinessUnitUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    code: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class BusinessUnit(BusinessUnitBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(default_factory=get_datetime_utc)
    users: list["User"] = Relationship(back_populates="business_unit")
    functions: list["Function"] = Relationship(back_populates="business_unit")
    files_visible: list["File"] = Relationship(back_populates="visible_bu")


class BusinessUnitPublic(BusinessUnitBase):
    id: uuid.UUID
    created_at: datetime | None = None


class BusinessUnitsPublic(SQLModel):
    data: list[BusinessUnitPublic]
    count: int


# Function models
class FunctionBase(SQLModel):
    name: str = Field(max_length=255)
    code: str = Field(max_length=50)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool = True
    business_unit_id: uuid.UUID = Field(foreign_key="businessunit.id")


class FunctionCreate(FunctionBase):
    pass


class FunctionUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    code: str | None = Field(default=None, max_length=50)
    description: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None
    business_unit_id: uuid.UUID | None = None


class Function(FunctionBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(default_factory=get_datetime_utc)
    business_unit: BusinessUnit = Relationship(back_populates="functions")
    users: list["User"] = Relationship(back_populates="function")
    files_uploaded: list["File"] = Relationship(back_populates="responsible_function")
    files_visible: list["File"] = Relationship(back_populates="visible_functions")


class FunctionPublic(FunctionBase):
    id: uuid.UUID
    created_at: datetime | None = None


class FunctionsPublic(SQLModel):
    data: list[FunctionPublic]
    count: int


# FileFunctionLink - Association table for File <-> Function many-to-many
# Must be defined before File since File references it
class FileFunctionLink(SQLModel, table=True):
    file_id: uuid.UUID = Field(
        foreign_key="file.id", primary_key=True, ondelete="CASCADE"
    )
    function_id: uuid.UUID = Field(
        foreign_key="function.id", primary_key=True, ondelete="CASCADE"
    )


# =============================================================================
# File Models
# =============================================================================

# Shared properties
class FileBase(SQLModel):
    filename: str = Field(max_length=255)
    original_filename: str = Field(max_length=255)
    content_type: str = Field(max_length=100)
    file_size: int
    responsible_function_id: uuid.UUID | None = Field(default=None, foreign_key="function.id")


class FileCreate(SQLModel):
    filename: str = Field(max_length=255)
    original_filename: str = Field(max_length=255)
    content_type: str = Field(max_length=100)
    file_size: int
    responsible_function_id: uuid.UUID | None = None
    visible_bu_id: uuid.UUID | None = None
    visible_function_ids: list[uuid.UUID] | None = None


class FileUpdate(SQLModel):
    filename: str | None = Field(default=None, max_length=255)


# Database model
class File(FileBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_utc,
        sa_type=DateTime(timezone=True),  # type: ignore
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    visible_bu_id: uuid.UUID | None = Field(default=None, foreign_key="businessunit.id")
    owner: User | None = Relationship(back_populates="files")
    responsible_function: "Function" = Relationship(back_populates="files_uploaded")
    visible_bu: "BusinessUnit" = Relationship(back_populates="files_visible")
    visible_functions: list["Function"] = Relationship(
        back_populates="files_visible", link_model=FileFunctionLink
    )


class FilePublic(FileBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class FilesPublic(SQLModel):
    data: list[FilePublic]
    count: int
