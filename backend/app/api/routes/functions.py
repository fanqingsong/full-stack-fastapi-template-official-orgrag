import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app import crud
from app.models import (
    Function,
    FunctionCreate,
    FunctionPublic,
    FunctionsPublic,
    FunctionUpdate,
    Message,
)

router = APIRouter(prefix="/functions", tags=["functions"])


@router.get("/", response_model=FunctionsPublic)
def read_functions(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
    business_unit_id: uuid.UUID | None = Query(None, description="Filter by business unit"),
) -> Any:
    """Retrieve all functions, optionally filtered by business unit."""
    if business_unit_id:
        funcs = crud.get_functions_by_bu(
            session=session, bu_id=business_unit_id, skip=skip, limit=limit
        )
        count = len(funcs)
    else:
        if current_user.is_superuser:
            count_statement = select(func.count()).select_from(Function)
            count = session.exec(count_statement).one()
        else:
            count_statement = (
                select(func.count())
                .select_from(Function)
                .where(Function.is_active == True)
            )
            count = session.exec(count_statement).one()
        funcs = crud.get_functions(session=session, skip=skip, limit=limit)

    return FunctionsPublic(data=funcs, count=count)


@router.get("/{func_id}", response_model=FunctionPublic)
def read_function(
    func_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """Get a specific function by ID."""
    func = crud.get_function_by_id(session=session, func_id=func_id)
    if not func:
        raise HTTPException(status_code=404, detail="Function not found")
    return func


@router.post(
    "/",
    response_model=FunctionPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def create_function(
    *,
    session: SessionDep,
    func_in: FunctionCreate,
) -> Any:
    """Create a new function (superuser only)."""
    # Verify business unit exists
    bu = crud.get_business_unit_by_id(session=session, bu_id=func_in.business_unit_id)
    if not bu:
        raise HTTPException(status_code=404, detail="Business unit not found")

    func = crud.create_function(session=session, func_in=func_in)
    return func


@router.patch(
    "/{func_id}",
    response_model=FunctionPublic,
    dependencies=[Depends(get_current_active_superuser)],
)
def update_function(
    *,
    session: SessionDep,
    func_id: uuid.UUID,
    func_in: FunctionUpdate,
) -> Any:
    """Update a function (superuser only)."""
    db_func = crud.get_function_by_id(session=session, func_id=func_id)
    if not db_func:
        raise HTTPException(status_code=404, detail="Function not found")

    if func_in.business_unit_id:
        bu = crud.get_business_unit_by_id(session=session, bu_id=func_in.business_unit_id)
        if not bu:
            raise HTTPException(status_code=404, detail="Business unit not found")

    func = crud.update_function(session=session, db_func=db_func, func_in=func_in)
    return func


@router.delete(
    "/{func_id}",
    dependencies=[Depends(get_current_active_superuser)],
)
def delete_function(
    *,
    session: SessionDep,
    func_id: uuid.UUID,
) -> Message:
    """Delete a function (superuser only)."""
    func = crud.get_function_by_id(session=session, func_id=func_id)
    if not func:
        raise HTTPException(status_code=404, detail="Function not found")
    crud.delete_function(session=session, db_func=func)
    return Message(message="Function deleted successfully")
