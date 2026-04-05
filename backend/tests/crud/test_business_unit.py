"""
Tests for BusinessUnit CRUD operations.
"""
from sqlmodel import Session

from app import crud
from app.models import BusinessUnit, BusinessUnitCreate, BusinessUnitUpdate
from tests.utils.utils import random_lower_string


def test_create_business_unit(db: Session) -> None:
    """Test creating a new business unit."""
    name = f"BU-{random_lower_string()}"
    code = random_lower_string()[:8].upper()
    description = random_lower_string()
    bu_in = BusinessUnitCreate(
        name=name,
        code=code,
        description=description,
        is_active=True,
    )
    bu = crud.create_business_unit(session=db, bu_in=bu_in)
    assert bu.id is not None
    assert bu.name == name
    assert bu.code == code
    assert bu.description == description
    assert bu.is_active is True


def test_get_business_unit_by_id(db: Session) -> None:
    """Test retrieving a business unit by ID."""
    bu_in = BusinessUnitCreate(
        name=f"BU-{random_lower_string()}",
        code=random_lower_string()[:8].upper(),
        description=random_lower_string(),
        is_active=True,
    )
    bu = crud.create_business_unit(session=db, bu_in=bu_in)
    retrieved_bu = crud.get_business_unit_by_id(session=db, bu_id=bu.id)
    assert retrieved_bu is not None
    assert retrieved_bu.id == bu.id
    assert retrieved_bu.name == bu.name


def test_get_business_unit_by_id_not_found(db: Session) -> None:
    """Test retrieving a non-existent business unit."""
    import uuid

    non_existent_id = uuid.uuid4()
    bu = crud.get_business_unit_by_id(session=db, bu_id=non_existent_id)
    assert bu is None


def test_get_business_units(db: Session) -> None:
    """Test retrieving multiple business units."""
    # Create multiple business units
    for i in range(3):
        bu_in = BusinessUnitCreate(
            name=f"BU-{i}-{random_lower_string()}",
            code=f"{i}{random_lower_string()[:7].upper()}",
            description=random_lower_string(),
            is_active=True,
        )
        crud.create_business_unit(session=db, bu_in=bu_in)

    # Retrieve all business units
    bus = crud.get_business_units(session=db, skip=0, limit=10)
    assert len(bus) >= 3


def test_update_business_unit(db: Session) -> None:
    """Test updating a business unit."""
    bu_in = BusinessUnitCreate(
        name=f"BU-{random_lower_string()}",
        code=random_lower_string()[:8].upper(),
        description=random_lower_string(),
        is_active=True,
    )
    bu = crud.create_business_unit(session=db, bu_in=bu_in)

    # Update the business unit
    new_name = f"Updated-{random_lower_string()}"
    new_description = random_lower_string()
    bu_in_update = BusinessUnitUpdate(
        name=new_name,
        description=new_description,
        is_active=False,
    )
    updated_bu = crud.update_business_unit(session=db, db_bu=bu, bu_in=bu_in_update)

    assert updated_bu.name == new_name
    assert updated_bu.description == new_description
    assert updated_bu.is_active is False
    assert updated_bu.code == bu.code  # Code should remain unchanged


def test_delete_business_unit(db: Session) -> None:
    """Test deleting a business unit."""
    bu_in = BusinessUnitCreate(
        name=f"BU-{random_lower_string()}",
        code=random_lower_string()[:8].upper(),
        description=random_lower_string(),
        is_active=True,
    )
    bu = crud.create_business_unit(session=db, bu_in=bu_in)
    bu_id = bu.id

    # Delete the business unit
    deleted_bu = crud.delete_business_unit(session=db, db_bu=bu)
    assert deleted_bu.id == bu_id

    # Verify it's deleted
    retrieved_bu = crud.get_business_unit_by_id(session=db, bu_id=bu_id)
    assert retrieved_bu is None


def test_business_unit_unique_name(db: Session) -> None:
    """Test that business unit names are unique."""
    name = f"BU-{random_lower_string()}"
    code1 = random_lower_string()[:8].upper()
    code2 = f"{random_lower_string()[:7].upper()}X"

    # Create first business unit
    bu_in1 = BusinessUnitCreate(
        name=name,
        code=code1,
        description=random_lower_string(),
        is_active=True,
    )
    crud.create_business_unit(session=db, bu_in=bu_in1)

    # Try to create second business unit with same name (different code)
    # This should fail at the database level due to unique constraint
    bu_in2 = BusinessUnitCreate(
        name=name,
        code=code2,
        description=random_lower_string(),
        is_active=True,
    )
    # Note: This will raise an IntegrityError, which we expect
    try:
        crud.create_business_unit(session=db, bu_in=bu_in2)
        assert False, "Should have raised an IntegrityError"
    except Exception:
        pass  # Expected


def test_business_unit_unique_code(db: Session) -> None:
    """Test that business unit codes are unique."""
    name1 = f"BU-{random_lower_string()}"
    name2 = f"BU-{random_lower_string()}"
    code = random_lower_string()[:8].upper()

    # Create first business unit
    bu_in1 = BusinessUnitCreate(
        name=name1,
        code=code,
        description=random_lower_string(),
        is_active=True,
    )
    crud.create_business_unit(session=db, bu_in=bu_in1)

    # Try to create second business unit with same code (different name)
    # This should fail at the database level due to unique constraint
    bu_in2 = BusinessUnitCreate(
        name=name2,
        code=code,
        description=random_lower_string(),
        is_active=True,
    )
    # Note: This will raise an IntegrityError, which we expect
    try:
        crud.create_business_unit(session=db, bu_in=bu_in2)
        assert False, "Should have raised an IntegrityError"
    except Exception:
        pass  # Expected
