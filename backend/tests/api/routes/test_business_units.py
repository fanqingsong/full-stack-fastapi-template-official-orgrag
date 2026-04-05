"""
Tests for Business Units API routes.
"""
import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import BusinessUnitCreate
from tests.utils.organization import create_random_business_unit
from tests.utils.utils import random_lower_string


def test_create_business_unit_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test creating a business unit as superuser."""
    name = f"BU-{random_lower_string()}"
    code = random_lower_string()[:8].upper()
    description = random_lower_string()

    data = {
        "name": name,
        "code": code,
        "description": description,
        "is_active": True,
    }
    response = client.post(
        f"{settings.API_V1_STR}/business-units/",
        headers=superuser_token_headers,
        json=data,
    )
    assert 200 <= response.status_code < 300

    content = response.json()
    assert content["name"] == name
    assert content["code"] == code
    assert content["description"] == description
    assert content["is_active"] is True
    assert "id" in content


def test_create_business_unit_as_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """Test that normal users cannot create business units."""
    data = {
        "name": f"BU-{random_lower_string()}",
        "code": random_lower_string()[:8].upper(),
        "description": random_lower_string(),
        "is_active": True,
    }
    response = client.post(
        f"{settings.API_V1_STR}/business-units/",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403


def test_read_business_units_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test reading all business units as superuser."""
    # Create some test business units
    for _ in range(3):
        create_random_business_unit(db)

    response = client.get(
        f"{settings.API_V1_STR}/business-units/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200

    content = response.json()
    assert "data" in content
    assert "count" in content
    assert len(content["data"]) >= 3


def test_read_business_units_as_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test reading active business units as normal user."""
    # Create active and inactive business units
    active_bu = create_random_business_unit(db)
    inactive_bu_in = BusinessUnitCreate(
        name=f"Inactive-BU-{random_lower_string()}",
        code="INACTIVE",
        description="Inactive business unit",
        is_active=False,
    )
    inactive_bu = crud.create_business_unit(session=db, bu_in=inactive_bu_in)

    response = client.get(
        f"{settings.API_V1_STR}/business-units/",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200

    content = response.json()
    assert "data" in content
    assert "count" in content

    # Normal user should only see active BUs
    bu_ids = [bu["id"] for bu in content["data"]]
    assert active_bu.id in bu_ids
    assert inactive_bu.id not in bu_ids


def test_read_business_unit_by_id_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test reading a specific business unit as superuser."""
    bu = create_random_business_unit(db)

    response = client.get(
        f"{settings.API_V1_STR}/business-units/{bu.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200

    content = response.json()
    assert content["id"] == bu.id
    assert content["name"] == bu.name
    assert content["code"] == bu.code


def test_read_business_unit_by_id_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test reading a non-existent business unit."""
    non_existent_id = uuid.uuid4()
    response = client.get(
        f"{settings.API_V1_STR}/business-units/{non_existent_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Business unit not found"}


def test_update_business_unit_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test updating a business unit as superuser."""
    bu = create_random_business_unit(db)

    new_name = f"Updated-{random_lower_string()}"
    new_description = random_lower_string()

    data = {
        "name": new_name,
        "description": new_description,
    }
    response = client.patch(
        f"{settings.API_V1_STR}/business-units/{bu.id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200

    content = response.json()
    assert content["name"] == new_name
    assert content["description"] == new_description
    assert content["id"] == bu.id


def test_update_business_unit_as_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test that normal users cannot update business units."""
    bu = create_random_business_unit(db)

    data = {"name": f"Hacked-{random_lower_string()}"}
    response = client.patch(
        f"{settings.API_V1_STR}/business-units/{bu.id}",
        headers=normal_user_token_headers,
        json=data,
    )
    assert response.status_code == 403


def test_update_business_unit_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test updating a non-existent business unit."""
    non_existent_id = uuid.uuid4()
    data = {"name": f"Updated-{random_lower_string()}"}
    response = client.patch(
        f"{settings.API_V1_STR}/business-units/{non_existent_id}",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Business unit not found"}


def test_delete_business_unit_as_superuser(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test deleting a business unit as superuser."""
    bu = create_random_business_unit(db)
    bu_id = bu.id

    response = client.delete(
        f"{settings.API_V1_STR}/business-units/{bu_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200

    content = response.json()
    assert content["message"] == "Business unit deleted successfully"

    # Verify it's deleted
    deleted_bu = crud.get_business_unit_by_id(session=db, bu_id=bu_id)
    assert deleted_bu is None


def test_delete_business_unit_as_normal_user(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test that normal users cannot delete business units."""
    bu = create_random_business_unit(db)

    response = client.delete(
        f"{settings.API_V1_STR}/business-units/{bu.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403

    # Verify it's NOT deleted
    existing_bu = crud.get_business_unit_by_id(session=db, bu_id=bu.id)
    assert existing_bu is not None


def test_delete_business_unit_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test deleting a non-existent business unit."""
    non_existent_id = uuid.uuid4()
    response = client.delete(
        f"{settings.API_V1_STR}/business-units/{non_existent_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Business unit not found"}


def test_business_units_pagination(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test pagination of business units."""
    # Create multiple business units
    for _ in range(5):
        create_random_business_unit(db)

    # Test pagination with skip and limit
    response = client.get(
        f"{settings.API_V1_STR}/business-units/?skip=0&limit=3",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200

    content = response.json()
    assert len(content["data"]) == 3

    # Test skip
    response2 = client.get(
        f"{settings.API_V1_STR}/business-units/?skip=3&limit=10",
        headers=superuser_token_headers,
    )
    assert response2.status_code == 200

    content2 = response2.json()
    # Should have fewer results since we skipped 3
    assert content2["count"] >= 5
