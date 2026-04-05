"""
Tests for Functions API routes.
"""
import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import FunctionCreate
from tests.utils.organization import create_random_business_unit, create_random_function
from tests.utils.utils import random_lower_string


def test_create_function_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test creating a function as superuser."""
    bu = create_random_business_unit(db)

    name = f"Function-{random_lower_string()}"
    code = random_lower_string()[:8].upper()
    description = random_lower_string()

    data = {
        "name": name,
        "code": code,
        "description": description,
        "is_active": True,
        "business_unit_id": str(bu.id),
    }
    response = client.post(
        f"{settings.API_V1_STR}/functions/",
        headers=superuser_token_headers,
        json=data,
    )
    assert 200 <= response.status_code < 300

    content = response.json()
    assert content["name"] == name
    assert content["code"] == code
    assert content["description"] == description
    assert content["is_active"] is True
    assert content["business_unit_id"] == str(bu.id)
    assert "id" in content


def test_create_function_as_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test that normal users cannot create functions."""
    bu = create_random_business_unit(db)

    data = {
        "name": f"Function-{random_lower_string()}",
        "code": random_lower_string()[:8].upper(),
        "description": random_lower_string(),
        "is_active": True,
        "business_unit_id": str(bu.id),
    }
    response = client.post(
        f"{settings.API_V1_STR}/functions/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403


def test_create_function_with_invalid_business_unit(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test creating a function with a non-existent business unit."""
    non_existent_bu_id = uuid.uuid4()

    data = {
        "name": f"Function-{random_lower_string()}",
        "code": random_lower_string()[:8].upper(),
        "description": random_lower_string(),
        "is_active": True,
        "business_unit_id": str(non_existent_bu_id),
    }
    response = client.post(
        f"{settings.API_V1_STR}/functions/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Business unit not found"}


def test_read_functions_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test reading all functions as superuser."""
    # Create some test functions
    for _ in range(3):
        create_random_function(db)

    response = client.get(
        f"{settings.API_V1_STR}/functions/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200

    content = response.json()
    assert "data" in content
    assert "count" in content
    assert len(content["data"]) >= 3


def test_read_functions_as_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test reading active functions as normal user."""
    # Create active and inactive functions
    bu = create_random_business_unit(db)

    active_func_in = FunctionCreate(
        name=f"Active-Function-{random_lower_string()}",
        code="ACTIVE",
        description="Active function",
        is_active=True,
        business_unit_id=bu.id,
    )
    active_func = crud.create_function(session=db, func_in=active_func_in)

    inactive_func_in = FunctionCreate(
        name=f"Inactive-Function-{random_lower_string()}",
        code="INACTIVE",
        description="Inactive function",
        is_active=False,
        business_unit_id=bu.id,
    )
    crud.create_function(session=db, func_in=inactive_func_in)

    response = client.get(
        f"{settings.API_V1_STR}/functions/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200

    content = response.json()
    assert "data" in content
    assert "count" in content

    # Normal user should only see active functions
    func_ids = [func["id"] for func in content["data"]]
    assert str(active_func.id) in func_ids


def test_read_functions_filtered_by_business_unit(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test reading functions filtered by business unit."""
    bu1 = create_random_business_unit(db)
    bu2 = create_random_business_unit(db)

    # Create functions for BU1
    func1_in = FunctionCreate(
        name=f"BU1-Function-{random_lower_string()}",
        code="BU1FUNC",
        description="Function for BU1",
        is_active=True,
        business_unit_id=bu1.id,
    )
    func1 = crud.create_function(session=db, func_in=func1_in)

    # Create functions for BU2
    func2_in = FunctionCreate(
        name=f"BU2-Function-{random_lower_string()}",
        code="BU2FUNC",
        description="Function for BU2",
        is_active=True,
        business_unit_id=bu2.id,
    )
    crud.create_function(session=db, func_in=func2_in)

    # Filter by BU1
    response = client.get(
        f"{settings.API_V1_STR}/functions/?business_unit_id={bu1.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200

    content = response.json()
    assert "data" in content
    assert len(content["data"]) == 1
    assert content["data"][0]["id"] == str(func1.id)
    assert content["data"][0]["business_unit_id"] == str(bu1.id)


def test_read_function_by_id(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test reading a specific function by ID."""
    func = create_random_function(db)

    response = client.get(
        f"{settings.API_V1_STR}/functions/{func.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200

    content = response.json()
    assert content["id"] == str(func.id)
    assert content["name"] == func.name
    assert content["code"] == func.code


def test_read_function_by_id_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test reading a non-existent function."""
    non_existent_id = uuid.uuid4()
    response = client.get(
        f"{settings.API_V1_STR}/functions/{non_existent_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Function not found"}


def test_update_function_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test updating a function as superuser."""
    func = create_random_function(db)

    new_name = f"Updated-{random_lower_string()}"
    new_description = random_lower_string()

    data = {
        "name": new_name,
        "description": new_description,
    }
    response = client.patch(
        f"{settings.API_V1_STR}/functions/{func.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200

    content = response.json()
    assert content["name"] == new_name
    assert content["description"] == new_description
    assert content["id"] == str(func.id)


def test_update_function_as_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test that normal users cannot update functions."""
    func = create_random_function(db)

    data = {"name": f"Hacked-{random_lower_string()}"}
    response = client.patch(
        f"{settings.API_V1_STR}/functions/{func.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403


def test_update_function_with_invalid_business_unit(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test updating a function with a non-existent business unit."""
    func = create_random_function(db)
    non_existent_bu_id = uuid.uuid4()

    data = {"business_unit_id": str(non_existent_bu_id)}
    response = client.patch(
        f"{settings.API_V1_STR}/functions/{func.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Business unit not found"}


def test_update_function_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test updating a non-existent function."""
    non_existent_id = uuid.uuid4()
    data = {"name": f"Updated-{random_lower_string()}"}
    response = client.patch(
        f"{settings.API_V1_STR}/functions/{non_existent_id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Function not found"}


def test_delete_function_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test deleting a function as superuser."""
    func = create_random_function(db)
    func_id = func.id

    response = client.delete(
        f"{settings.API_V1_STR}/functions/{func_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200

    content = response.json()
    assert content["message"] == "Function deleted successfully"

    # Verify it's deleted
    deleted_func = crud.get_function_by_id(session=db, func_id=func_id)
    assert deleted_func is None


def test_delete_function_as_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test that normal users cannot delete functions."""
    func = create_random_function(db)

    response = client.delete(
        f"{settings.API_V1_STR}/functions/{func.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403

    # Verify it's NOT deleted
    existing_func = crud.get_function_by_id(session=db, func_id=func.id)
    assert existing_func is not None


def test_delete_function_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test deleting a non-existent function."""
    non_existent_id = uuid.uuid4()
    response = client.delete(
        f"{settings.API_V1_STR}/functions/{non_existent_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Function not found"}


def test_functions_pagination(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test pagination of functions."""
    # Create multiple functions
    for _ in range(5):
        create_random_function(db)

    # Test pagination with skip and limit
    response = client.get(
        f"{settings.API_V1_STR}/functions/?skip=0&limit=3",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200

    content = response.json()
    assert len(content["data"]) == 3

    # Test skip
    response2 = client.get(
        f"{settings.API_V1_STR}/functions/?skip=3&limit=10",
        headers=superuser_token_headers,
    )
    assert response2.status_code == 200

    content2 = response2.json()
    # Should have fewer results since we skipped 3
    assert content2["count"] >= 5
