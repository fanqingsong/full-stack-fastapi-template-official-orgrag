"""
Tests for file access control and permissions.
"""
import uuid

from sqlmodel import Session

from app import crud
from app.models import (
    BusinessUnitCreate,
    File,
    FileCreate,
    FileFunctionLink,
    FunctionCreate,
    User,
    UserCreate,
)
from tests.utils.utils import random_email, random_lower_string


def create_test_user_with_org(
    db: Session,
    email: str,
    business_unit_id: uuid.UUID | None = None,
    function_id: uuid.UUID | None = None,
) -> User:
    """Helper to create a test user with optional business unit and function assignments."""
    user_in = UserCreate(
        email=email,
        password=random_lower_string(),
        full_name=random_lower_string(),
        business_unit_id=business_unit_id,
        function_id=function_id,
    )
    return crud.create_user(session=db, user_create=user_in)


def create_test_file(
    db: Session,
    owner: User,
    visible_bu_id: uuid.UUID | None = None,
    responsible_function_id: uuid.UUID | None = None,
    visible_function_ids: list[uuid.UUID] | None = None,
) -> File:
    """Helper to create a test file with specific visibility settings."""
    file_in = FileCreate(
        filename=random_lower_string(),
        original_filename=random_lower_string(),
        content_type="text/plain",
        file_size=1024,
        visible_bu_id=visible_bu_id,
        responsible_function_id=responsible_function_id,
        visible_function_ids=visible_function_ids,
    )
    file = File.model_validate(file_in, update={"owner_id": owner.id})
    db.add(file)
    db.flush()

    # Handle many-to-many relationships
    if visible_function_ids:
        for func_id in visible_function_ids:
            link = FileFunctionLink(file_id=file.id, function_id=func_id)
            db.add(link)

    db.commit()
    db.refresh(file)
    return file


def test_file_access_owner(db: Session) -> None:
    """Test that file owner can access their own files."""
    user = create_test_user_with_org(db, random_email())
    file = create_test_file(db, user)

    has_access = crud.check_file_access(session=db, file=file, user=user)
    assert has_access is True


def test_file_access_superuser(db: Session) -> None:
    """Test that superuser can access any file."""
    superuser = create_test_user_with_org(db, random_email())
    superuser.is_superuser = True
    db.commit()

    normal_user = create_test_user_with_org(db, random_email())
    file = create_test_file(db, normal_user)

    has_access = crud.check_file_access(session=db, file=file, user=superuser)
    assert has_access is True


def test_file_access_no_restrictions(db: Session) -> None:
    """Test that files with no restrictions are NOT accessible to non-owners (secure by default)."""
    owner = create_test_user_with_org(db, random_email())
    other_user = create_test_user_with_org(db, random_email())

    # Create file with no visibility restrictions
    file = create_test_file(db, owner, visible_bu_id=None, visible_function_ids=None)

    # Other user should NOT have access (secure by default)
    has_access = crud.check_file_access(session=db, file=file, user=other_user)
    assert has_access is False


def test_file_access_by_business_unit(db: Session) -> None:
    """Test file access control via business unit visibility."""
    # Create business units
    bu1_in = BusinessUnitCreate(
        name=f"BU1-{random_lower_string()}",
        code="BU1",
        description="Business Unit 1",
        is_active=True,
    )
    bu1 = crud.create_business_unit(session=db, bu_in=bu1_in)

    bu2_in = BusinessUnitCreate(
        name=f"BU2-{random_lower_string()}",
        code="BU2",
        description="Business Unit 2",
        is_active=True,
    )
    bu2 = crud.create_business_unit(session=db, bu_in=bu2_in)

    # Create users in different business units
    user1 = create_test_user_with_org(db, random_email(), business_unit_id=bu1.id)
    user2 = create_test_user_with_org(db, random_email(), business_unit_id=bu2.id)

    # Create file visible only to BU1
    file = create_test_file(db, user1, visible_bu_id=bu1.id)

    # User1 (same BU) should have access
    has_access_user1 = crud.check_file_access(session=db, file=file, user=user1)
    assert has_access_user1 is True

    # User2 (different BU) should NOT have access
    has_access_user2 = crud.check_file_access(session=db, file=file, user=user2)
    assert has_access_user2 is False


def test_file_access_by_function(db: Session) -> None:
    """Test file access control via function visibility."""
    # Create business unit and functions
    bu_in = BusinessUnitCreate(
        name=f"BU-{random_lower_string()}",
        code="BU",
        description="Business Unit",
        is_active=True,
    )
    bu = crud.create_business_unit(session=db, bu_in=bu_in)

    func1_in = FunctionCreate(
        name=f"Func1-{random_lower_string()}",
        code="FUNC1",
        description="Function 1",
        is_active=True,
        business_unit_id=bu.id,
    )
    func1 = crud.create_function(session=db, func_in=func1_in)

    func2_in = FunctionCreate(
        name=f"Func2-{random_lower_string()}",
        code="FUNC2",
        description="Function 2",
        is_active=True,
        business_unit_id=bu.id,
    )
    func2 = crud.create_function(session=db, func_in=func2_in)

    # Create users with different functions
    user1 = create_test_user_with_org(db, random_email(), business_unit_id=bu.id, function_id=func1.id)
    user2 = create_test_user_with_org(db, random_email(), business_unit_id=bu.id, function_id=func2.id)

    # Create file visible only to func1
    file = create_test_file(db, user1, visible_function_ids=[func1.id])

    # User1 (same function) should have access
    has_access_user1 = crud.check_file_access(session=db, file=file, user=user1)
    assert has_access_user1 is True

    # User2 (different function) should NOT have access
    has_access_user2 = crud.check_file_access(session=db, file=file, user=user2)
    assert has_access_user2 is False


def test_file_access_multiple_functions(db: Session) -> None:
    """Test file access control with multiple visible functions."""
    # Create business unit and functions
    bu_in = BusinessUnitCreate(
        name=f"BU-{random_lower_string()}",
        code="BU",
        description="Business Unit",
        is_active=True,
    )
    bu = crud.create_business_unit(session=db, bu_in=bu_in)

    func1_in = FunctionCreate(
        name=f"Func1-{random_lower_string()}",
        code="FUNC1",
        description="Function 1",
        is_active=True,
        business_unit_id=bu.id,
    )
    func1 = crud.create_function(session=db, func_in=func1_in)

    func2_in = FunctionCreate(
        name=f"Func2-{random_lower_string()}",
        code="FUNC2",
        description="Function 2",
        is_active=True,
        business_unit_id=bu.id,
    )
    func2 = crud.create_function(session=db, func_in=func2_in)

    func3_in = FunctionCreate(
        name=f"Func3-{random_lower_string()}",
        code="FUNC3",
        description="Function 3",
        is_active=True,
        business_unit_id=bu.id,
    )
    func3 = crud.create_function(session=db, func_in=func3_in)

    # Create users with different functions
    user1 = create_test_user_with_org(db, random_email(), business_unit_id=bu.id, function_id=func1.id)
    user2 = create_test_user_with_org(db, random_email(), business_unit_id=bu.id, function_id=func2.id)
    user3 = create_test_user_with_org(db, random_email(), business_unit_id=bu.id, function_id=func3.id)

    # Create file visible to func1 and func2
    file = create_test_file(db, user1, visible_function_ids=[func1.id, func2.id])

    # User1 and User2 should have access
    assert crud.check_file_access(session=db, file=file, user=user1) is True
    assert crud.check_file_access(session=db, file=file, user=user2) is True

    # User3 should NOT have access
    assert crud.check_file_access(session=db, file=file, user=user3) is False


def test_file_access_user_without_function(db: Session) -> None:
    """Test file access when user has no function assigned."""
    # Create business unit and function
    bu_in = BusinessUnitCreate(
        name=f"BU-{random_lower_string()}",
        code="BU",
        description="Business Unit",
        is_active=True,
    )
    bu = crud.create_business_unit(session=db, bu_in=bu_in)

    func_in = FunctionCreate(
        name=f"Func-{random_lower_string()}",
        code="FUNC",
        description="Function",
        is_active=True,
        business_unit_id=bu.id,
    )
    func = crud.create_function(session=db, func_in=func_in)

    # Create users - one with function, one without
    user_with_func = create_test_user_with_org(
        db, random_email(), business_unit_id=bu.id, function_id=func.id
    )
    user_without_func = create_test_user_with_org(db, random_email(), business_unit_id=bu.id)

    # Create file visible only to the function
    file = create_test_file(db, user_with_func, visible_function_ids=[func.id])

    # User with function should have access
    assert crud.check_file_access(session=db, file=file, user=user_with_func) is True

    # User without function should NOT have access
    assert crud.check_file_access(session=db, file=file, user=user_without_func) is False


def test_file_access_mixed_visibility(db: Session) -> None:
    """Test file access with both BU and function visibility set."""
    # Create business units and functions
    bu1_in = BusinessUnitCreate(
        name=f"BU1-{random_lower_string()}",
        code="BU1",
        description="Business Unit 1",
        is_active=True,
    )
    bu1 = crud.create_business_unit(session=db, bu_in=bu1_in)

    bu2_in = BusinessUnitCreate(
        name=f"BU2-{random_lower_string()}",
        code="BU2",
        description="Business Unit 2",
        is_active=True,
    )
    bu2 = crud.create_business_unit(session=db, bu_in=bu2_in)

    func1_in = FunctionCreate(
        name=f"Func1-{random_lower_string()}",
        code="FUNC1",
        description="Function 1",
        is_active=True,
        business_unit_id=bu1.id,
    )
    func1 = crud.create_function(session=db, func_in=func1_in)

    func2_in = FunctionCreate(
        name=f"Func2-{random_lower_string()}",
        code="FUNC2",
        description="Function 2",
        is_active=True,
        business_unit_id=bu1.id,
    )
    func2 = crud.create_function(session=db, func_in=func2_in)

    # Create users
    user1_bu1_func1 = create_test_user_with_org(
        db, random_email(), business_unit_id=bu1.id, function_id=func1.id
    )
    user2_bu1_func2 = create_test_user_with_org(
        db, random_email(), business_unit_id=bu1.id, function_id=func2.id
    )
    user3_bu2 = create_test_user_with_org(db, random_email(), business_unit_id=bu2.id)

    # Create file visible to BU1 AND func1 (both conditions set)
    file = create_test_file(db, user1_bu1_func1, visible_bu_id=bu1.id, visible_function_ids=[func1.id])

    # User1 (matches both BU and function) should have access
    assert crud.check_file_access(session=db, file=file, user=user1_bu1_func1) is True

    # User2 (matches BU but not function) should have access via BU
    assert crud.check_file_access(session=db, file=file, user=user2_bu1_func2) is True

    # User3 (doesn't match BU) should NOT have access
    assert crud.check_file_access(session=db, file=file, user=user3_bu2) is False
