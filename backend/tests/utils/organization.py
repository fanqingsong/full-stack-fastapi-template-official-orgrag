"""
Utility functions for creating test business units and functions.
"""
import uuid

from sqlmodel import Session

from app import crud
from app.models import BusinessUnit, BusinessUnitCreate, Function, FunctionCreate
from tests.utils.utils import random_lower_string


def create_random_business_unit(db: Session) -> BusinessUnit:
    """Create a random business unit for testing."""
    bu_in = BusinessUnitCreate(
        name=f"BU-{random_lower_string()[:8]}",
        code=random_lower_string()[:8].upper(),
        description=f"Test business unit {random_lower_string()}",
        is_active=True,
    )
    return crud.create_business_unit(session=db, bu_in=bu_in)


def create_random_function(db: Session, business_unit_id: uuid.UUID | None = None) -> Function:
    """Create a random function for testing.

    If business_unit_id is not provided, creates a new business unit first.
    """
    if business_unit_id is None:
        bu = create_random_business_unit(db)
        business_unit_id = bu.id

    func_in = FunctionCreate(
        name=f"Function-{random_lower_string()[:8]}",
        code=random_lower_string()[:8].upper(),
        description=f"Test function {random_lower_string()}",
        is_active=True,
        business_unit_id=business_unit_id,
    )
    return crud.create_function(session=db, func_in=func_in)
