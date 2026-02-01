import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app import crud
from app.models import (
    BusinessUnit,
    BusinessUnitCreate,
    BusinessUnitPublic,
    BusinessUnitsPublic,
    BusinessUnitUpdate,
    Message,
)

router = APIRouter(prefix="/business-units", tags=["business-units"])


@router.get("/", response_model=BusinessUnitsPublic)
def read_business_units(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve all business units."""
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(BusinessUnit)
        count = session.exec(count_statement).one()
        statement = select(BusinessUnit).offset(skip).limit(limit)
        bus = session.exec(statement).all()
    else:
        # Non-superusers can only see active BUs
        count_statement = (
            select(func.count())
            .select_from(BusinessUnit)
            .where(BusinessUnit.is_active == True)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(BusinessUnit)
            .where(BusinessUnit.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        bus = session.exec(statement).all()

    return BusinessUnitsPublic(data=bus, count=count)


@router.get("/{bu_id}", response_model=BusinessUnitPublic)
def read_business_unit(
    bu_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Get a specific business unit by ID."""
    bu = crud.get_business_unit_by_id(session=session, bu_id=bu_id)
    if not bu:
        raise HTTPException(status_code=404, detail="Business unit not found")
    return bu


@router.post(
    "/",
    response_model=BusinessUnitPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_business_unit(
    *,
    session: SessionDep,
    bu_in: BusinessUnitCreate,
) -> Any:
    """Create a new business unit (superuser only)."""
    bu = crud.create_business_unit(session=session, bu_in=bu_in)
    return bu


@router.patch(
    "/{bu_id}",
    response_model=BusinessUnitPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def update_business_unit(
    *,
    session: SessionDep,
    bu_id: uuid.UUID,
    bu_in: BusinessUnitUpdate,
) -> Any:
    """Update a business unit (superuser only)."""
    db_bu = crud.get_business_unit_by_id(session=session, bu_id=bu_id)
    if not db_bu:
        raise HTTPException(status_code=404, detail="Business unit not found")
    bu = crud.update_business_unit(session=session, db_bu=db_bu, bu_in=bu_in)
    return bu


@router.delete(
    "/{bu_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_business_unit(
    *,
    session: SessionDep,
    bu_id: uuid.UUID,
) -> Message:
    """Delete a business unit (superuser only)."""
    bu = crud.get_business_unit_by_id(session=session, bu_id=bu_id)
    if not bu:
        raise HTTPException(status_code=404, detail="Business unit not found")
    crud.delete_business_unit(session=session, db_bu=bu)
    return Message(message="Business unit deleted successfully")
