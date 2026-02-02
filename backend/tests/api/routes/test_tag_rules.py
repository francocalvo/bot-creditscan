"""API tests for tag rules."""

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings


def test_create_tag_rule(
    client: TestClient, _db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    """Test creating a tag rule."""
    # First create a tag
    tag_data = {
        "label": "Shopping",
    }
    tag_response = client.post(
        f"{settings.API_V1_STR}/tags/",
        json=tag_data,
        headers=normal_user_token_headers,
    )
    assert tag_response.status_code == 201
    tag_id = tag_response.json()["tag_id"]

    # Create a tag rule
    rule_data = {
        "tag_id": str(tag_id),
        "name": "Amazon purchases",
        "payee_contains": "amazon",
        "enabled": True,
        "priority": 100,
    }
    response = client.post(
        f"{settings.API_V1_STR}/tag-rules/",
        json=rule_data,
        headers=normal_user_token_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["tag_id"] == tag_id
    assert data["name"] == "Amazon purchases"
    assert data["payee_contains"] == "amazon"
    assert data["enabled"] is True
    assert data["priority"] == 100
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_tag_rule_no_conditions_fails(
    client: TestClient, _db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    """Test creating a tag rule with no conditions fails."""
    # First create a tag
    tag_data = {
        "label": "Shopping",
    }
    tag_response = client.post(
        f"{settings.API_V1_STR}/tags/",
        json=tag_data,
        headers=normal_user_token_headers,
    )
    assert tag_response.status_code == 201
    tag_id = tag_response.json()["tag_id"]

    # Try to create a rule with no conditions
    rule_data = {
        "tag_id": str(tag_id),
        "name": "Empty rule",
    }
    response = client.post(
        f"{settings.API_V1_STR}/tag-rules/",
        json=rule_data,
        headers=normal_user_token_headers,
    )

    assert response.status_code == 422  # Validation error


def test_create_tag_rule_invalid_regex_fails(
    client: TestClient, _db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    """Test creating a tag rule with invalid regex fails."""
    # First create a tag
    tag_data = {
        "label": "Shopping",
    }
    tag_response = client.post(
        f"{settings.API_V1_STR}/tags/",
        json=tag_data,
        headers=normal_user_token_headers,
    )
    assert tag_response.status_code == 201
    tag_id = tag_response.json()["tag_id"]

    # Try to create a rule with invalid regex
    rule_data = {
        "tag_id": str(tag_id),
        "payee_regex": "[invalid(",  # Invalid regex
    }
    response = client.post(
        f"{settings.API_V1_STR}/tag-rules/",
        json=rule_data,
        headers=normal_user_token_headers,
    )

    assert response.status_code == 422  # Validation error


def test_list_tag_rules(
    client: TestClient, _db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    """Test listing tag rules."""
    # First create a tag
    tag_data = {
        "label": "Shopping",
    }
    tag_response = client.post(
        f"{settings.API_V1_STR}/tags/",
        json=tag_data,
        headers=normal_user_token_headers,
    )
    assert tag_response.status_code == 201
    tag_id = tag_response.json()["tag_id"]

    # Create multiple rules
    for i in range(3):
        rule_data = {
            "tag_id": str(tag_id),
            "name": f"Rule {i}",
            "payee_contains": f"test{i}",
            "priority": i,
        }
        response = client.post(
            f"{settings.API_V1_STR}/tag-rules/",
            json=rule_data,
            headers=normal_user_token_headers,
        )
        assert response.status_code == 201

    # List rules
    response = client.get(
        f"{settings.API_V1_STR}/tag-rules/",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 3
    assert len(data["data"]) == 3


def test_get_tag_rule(
    client: TestClient, _db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    """Test getting a specific tag rule."""
    # First create a tag
    tag_data = {
        "label": "Shopping",
    }
    tag_response = client.post(
        f"{settings.API_V1_STR}/tags/",
        json=tag_data,
        headers=normal_user_token_headers,
    )
    assert tag_response.status_code == 201
    tag_id = tag_response.json()["tag_id"]

    # Create a rule
    rule_data = {
        "tag_id": str(tag_id),
        "name": "Test rule",
        "payee_contains": "amazon",
    }
    create_response = client.post(
        f"{settings.API_V1_STR}/tag-rules/",
        json=rule_data,
        headers=normal_user_token_headers,
    )
    assert create_response.status_code == 201
    rule_id = create_response.json()["id"]

    # Get the rule
    response = client.get(
        f"{settings.API_V1_STR}/tag-rules/{rule_id}",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == rule_id
    assert data["name"] == "Test rule"


def test_get_tag_rule_unauthorized(
    client: TestClient, _db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    """Test that users can't access other users' tag rules."""
    # Create a second user
    user2_response = client.post(
        f"{settings.API_V1_STR}/users/",
        json={
            "email": "user2@example.com",
            "password": "password123",
            "full_name": "User Two",
        },
    )
    assert user2_response.status_code == 200

    # Login as second user
    login_response = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={
            "username": "user2@example.com",
            "password": "password123",
        },
    )
    assert login_response.status_code == 200
    user2_token = login_response.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}

    # First user creates a tag and rule
    tag_data = {
        "label": "Shopping",
    }
    tag_response = client.post(
        f"{settings.API_V1_STR}/tags/",
        json=tag_data,
        headers=normal_user_token_headers,
    )
    assert tag_response.status_code == 201
    tag_id = tag_response.json()["tag_id"]

    rule_data = {
        "tag_id": str(tag_id),
        "name": "Test rule",
        "payee_contains": "amazon",
    }
    create_response = client.post(
        f"{settings.API_V1_STR}/tag-rules/",
        json=rule_data,
        headers=normal_user_token_headers,
    )
    assert create_response.status_code == 201
    rule_id = create_response.json()["id"]

    # Second user tries to get first user's rule
    response = client.get(
        f"{settings.API_V1_STR}/tag-rules/{rule_id}",
        headers=user2_headers,
    )

    assert response.status_code == 403


def test_update_tag_rule(
    client: TestClient, _db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    """Test updating a tag rule."""
    # First create a tag
    tag_data = {
        "label": "Shopping",
    }
    tag_response = client.post(
        f"{settings.API_V1_STR}/tags/",
        json=tag_data,
        headers=normal_user_token_headers,
    )
    assert tag_response.status_code == 201
    tag_id = tag_response.json()["tag_id"]

    # Create a rule
    rule_data = {
        "tag_id": str(tag_id),
        "name": "Test rule",
        "payee_contains": "amazon",
    }
    create_response = client.post(
        f"{settings.API_V1_STR}/tag-rules/",
        json=rule_data,
        headers=normal_user_token_headers,
    )
    assert create_response.status_code == 201
    rule_id = create_response.json()["id"]

    # Update the rule
    update_data = {
        "name": "Updated rule",
        "enabled": False,
        "priority": 50,
    }
    response = client.patch(
        f"{settings.API_V1_STR}/tag-rules/{rule_id}",
        json=update_data,
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated rule"
    assert data["enabled"] is False
    assert data["priority"] == 50


def test_delete_tag_rule(
    client: TestClient, _db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    """Test deleting a tag rule."""
    # First create a tag
    tag_data = {
        "label": "Shopping",
    }
    tag_response = client.post(
        f"{settings.API_V1_STR}/tags/",
        json=tag_data,
        headers=normal_user_token_headers,
    )
    assert tag_response.status_code == 201
    tag_id = tag_response.json()["tag_id"]

    # Create a rule
    rule_data = {
        "tag_id": str(tag_id),
        "name": "Test rule",
        "payee_contains": "amazon",
    }
    create_response = client.post(
        f"{settings.API_V1_STR}/tag-rules/",
        json=rule_data,
        headers=normal_user_token_headers,
    )
    assert create_response.status_code == 201
    rule_id = create_response.json()["id"]

    # Delete the rule
    response = client.delete(
        f"{settings.API_V1_STR}/tag-rules/{rule_id}",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 204

    # Verify rule is deleted
    get_response = client.get(
        f"{settings.API_V1_STR}/tag-rules/{rule_id}",
        headers=normal_user_token_headers,
    )
    assert get_response.status_code == 404


def test_apply_rules_dry_run(
    client: TestClient, _db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    """Test applying rules in dry run mode."""
    # Setup: Create a credit card, statement, and transaction
    # (This would need proper setup; for now, we'll test the API endpoint exists)

    # First create a tag
    tag_data = {
        "label": "Shopping",
    }
    tag_response = client.post(
        f"{settings.API_V1_STR}/tags/",
        json=tag_data,
        headers=normal_user_token_headers,
    )
    assert tag_response.status_code == 201

    # Apply rules in dry run mode
    request_data = {
        "dry_run": True,
    }
    response = client.post(
        f"{settings.API_V1_STR}/tag-rules/apply",
        json=request_data,
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert "evaluated_count" in data
    assert "applied_count" in data


def test_list_tag_rules_with_filters(
    client: TestClient, _db: Session, normal_user_token_headers: dict[str, str]
) -> None:
    """Test listing tag rules with filters."""
    # First create a tag
    tag_data = {
        "label": "Shopping",
    }
    tag_response = client.post(
        f"{settings.API_V1_STR}/tags/",
        json=tag_data,
        headers=normal_user_token_headers,
    )
    assert tag_response.status_code == 201
    tag_id = tag_response.json()["tag_id"]

    # Create enabled and disabled rules
    rule1_data = {
        "tag_id": str(tag_id),
        "name": "Enabled rule",
        "payee_contains": "amazon",
        "enabled": True,
    }
    client.post(
        f"{settings.API_V1_STR}/tag-rules/",
        json=rule1_data,
        headers=normal_user_token_headers,
    )

    rule2_data = {
        "tag_id": str(tag_id),
        "name": "Disabled rule",
        "payee_contains": "netflix",
        "enabled": False,
    }
    client.post(
        f"{settings.API_V1_STR}/tag-rules/",
        json=rule2_data,
        headers=normal_user_token_headers,
    )

    # List only enabled rules
    response = client.get(
        f"{settings.API_V1_STR}/tag-rules/?enabled=true",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["data"][0]["name"] == "Enabled rule"

    # List only disabled rules
    response = client.get(
        f"{settings.API_V1_STR}/tag-rules/?enabled=false",
        headers=normal_user_token_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 1
    assert data["data"][0]["name"] == "Disabled rule"
