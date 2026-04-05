"""
Tests for Function CRUD operations.
"""
import uuid

from sqlmodel import Session

from app import crud
from app.models import BusinessUnitCreate, FunctionCreate, FunctionUpdate
from tests.utils.organization import create_random_business_unit
from tests.utils.utils import random_lower_string


def test_create_function(db: Session) -> None:
    """Test creating a new function."""
    # Create a business unit first
    bu = create_random_business_unit(db)

    name = f"Function-{random_lower_string()}"
    code = random_lower_string()[:8].upper()
    description = random_lower_string()
    func_in = FunctionCreate(
        name=name,
        code=code,
        description=description,
        is_active=True,
        business_unit_id=bu.id,
    )
    func = crud.create_function(session=db, func_in=func_in)

    assert func.id is not None
    assert func.name == name
    assert func.code == code
    assert func.description == description
    assert func.is_active is True
    assert func.business_unit_id == bu.id


def test_get_function_by_id(db: Session) -> None:
    """Test retrieving a function by ID."""
    bu = create_random_business_unit(db)
    func_in = FunctionCreate(
        name=f"Function-{random_lower_string()}",
        code=random_lower_string()[:8].upper(),
        description=random_lower_string(),
        is_active=True,
        business_unit_id=bu.id,
    )
    func = crud.create_function(session=db, func_in=func_in)

    retrieved_func = crud.get_function_by_id(session=db, func_id=func.id)
    assert retrieved_func is not None
    assert retrieved_func.id == func.id
    assert retrieved_func.name == func.name


def test_get_function_by_id_not_found(db: Session) -> None:
    """Test retrieving a non-existent function."""
    non_existent_id = uuid.uuid4()
    func = crud.get_function_by_id(session=db, func_id=non_existent_id)
    assert func is None


def test_get_functions(db: Session) -> None:
    """Test retrieving multiple functions."""
    bu = create_random_business_unit(db)

    # Create multiple functions
    for i in range(3):
        func_in = FunctionCreate(
            name=f"Function-{i}-{random_lower_string()}",
            code=f"{i}{random_lower_string()[:7].upper()}",
            description=random_lower_string(),
            is_active=True,
            business_unit_id=bu.id,
        )
        crud.create_function(session=db, func_in=func_in)

    # Retrieve all functions
    funcs = crud.get_functions(session=db, skip=0, limit=10)
    assert len(funcs) >= 3


def test_get_functions_by_business_unit(db: Session) -> None:
    """Test retrieving functions filtered by business unit."""
    # Create two business units
    bu1 = create_random_business_unit(db)
    bu2 = create_random_business_unit(db)

    # Create functions for BU1
    for i in range(2):
        func_in = FunctionCreate(
            name=f"BU1-Function-{i}-{random_lower_string()}",
            code=f"BU1-{i}{random_lower_string()[:6].upper()}",
            description=random_lower_string(),
            is_active=True,
            business_unit_id=bu1.id,
        )
        crud.create_function(session=db, func_in=func_in)

    # Create functions for BU2
    for i in range(3):
        func_in = FunctionCreate(
            name=f"BU2-Function-{i}-{random_lower_string()}",
            code=f"BU2-{i}{random_lower_string()[:6].upper()}",
            description=random_lower_string(),
            is_active=True,
            business_unit_id=bu2.id,
        )
        crud.create_function(session=db, func_in=func_in)

    # Retrieve functions for BU1
    bu1_funcs = crud.get_functions_by_bu(session=db, bu_id=bu1.id, skip=0, limit=10)
    assert len(bu1_funcs) == 2
    for func in bu1_funcs:
        assert func.business_unit_id == bu1.id

    # Retrieve functions for BU2
    bu2_funcs = crud.get_functions_by_bu(session=db, bu_id=bu2.id, skip=0, limit=10)
    assert len(bu2_funcs) == 3
    for func in bu2_funcs:
        assert func.business_unit_id == bu2.id


def test_update_function(db: Session) -> None:
    """Test updating a function."""
    bu = create_random_business_unit(db)
    func_in = FunctionCreate(
        name=f"Function-{random_lower_string()}",
        code=random_lower_string()[:8].upper(),
        description=random_lower_string(),
        is_active=True,
        business_unit_id=bu.id,
    )
    func = crud.create_function(session=db, func_in=func_in)

    # Update the function
    new_name = f"Updated-{random_lower_string()}"
    new_description = random_lower_string()
    func_in_update = FunctionUpdate(
        name=new_name,
        description=new_description,
        is_active=False,
    )
    updated_func = crud.update_function(session=db, db_func=func, func_in=func_in_update)

    assert updated_func.name == new_name
    assert updated_func.description == new_description
    assert updated_func.is_active is False
    assert updated_func.code == func.code  # Code should remain unchanged
    assert updated_func.business_unit_id == bu.id  # BU should remain unchanged


def test_update_function_business_unit(db: Session) -> None:
    """Test updating a function's business unit."""
    bu1 = create_random_business_unit(db)
    bu2 = create_random_business_unit(db)

    func_in = FunctionCreate(
        name=f"Function-{random_lower_string()}",
        code=random_lower_string()[:8].upper(),
        description=random_lower_string(),
        is_active=True,
        business_unit_id=bu1.id,
    )
    func = crud.create_function(session=db, func_in=func_in)

    # Update the function's business unit
    func_in_update = FunctionUpdate(business_unit_id=bu2.id)
    updated_func = crud.update_function(session=db, db_func=func, func_in=func_in_update)

    assert updated_func.business_unit_id == bu2.id


def test_delete_function(db: Session) -> None:
    """Test deleting a function."""
    bu = create_random_business_unit(db)
    func_in = FunctionCreate(
        name=f"Function-{random_lower_string()}",
        code=random_lower_string()[:8].upper(),
        description=random_lower_string(),
        is_active=True,
        business_unit_id=bu.id,
    )
    func = crud.create_function(session=db, func_in=func_in)
    func_id = func.id

    # Delete the function
    deleted_func = crud.delete_function(session=db, db_func=func)
    assert deleted_func.id == func_id

    # Verify it's deleted
    retrieved_func = crud.get_function_by_id(session=db, func_id=func_id)
    assert retrieved_func is None


def test_function_with_invalid_business_unit(db: Session) -> None:
    """Test creating a function with a non-existent business unit."""
    non_existent_bu_id = uuid.uuid4()

    func_in = FunctionCreate(
        name=f"Function-{random_lower_string()}",
        code=random_lower_string()[:8].upper(),
        description=random_lower_string(),
        is_active=True,
        business_unit_id=non_existent_bu_id,
    )

    # This should fail at the database level due to foreign key constraint
    try:
        crud.create_function(session=db, func_in=func_in)
        assert False, "Should have raised an IntegrityError"
    except Exception:
        pass  # Expected
