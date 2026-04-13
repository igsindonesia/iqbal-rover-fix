import io
import os
import uuid
import pytest
from src.users.models import User
from main import app
from src.core.auth import get_current_user
from tests.utils import * 

# ========================
# Override dependency
# ========================
@pytest.fixture
def override_current_user(test_user):
    app.dependency_overrides[get_current_user] = lambda: test_user
    yield
    app.dependency_overrides.clear()


# ========================
# TESTING POST Feature
# ========================
def test_upload_valid_image(test_client, test_db, test_user, override_current_user):
    file_content = io.BytesIO(b"fake_image_content")

    response = test_client.post(
        f"/posts/{test_user.user_id}",
        files={"file": ("public/8ff23fa2267e4af3c344bcf9a695c41e.jpg", file_content, "image/jpeg")}
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user_id"] == test_user.user_id
    assert data["image_url"].endswith(".jpg")
    assert os.path.exists(data["image_url"])


def test_upload_invalid_extension(test_client, test_db, test_user, override_current_user):
    file_content = io.BytesIO(b"fake_gif_content")
    response = test_client.post(
        f"/posts/{test_user.user_id}",
        files={"file": ("public\8498bc9d90c7b153c30ee2aa8ec4f0c2.gif", file_content, "image/gif")}
    )

    assert response.status_code == 400, response.text
    assert "not allowed" in response.json()["detail"].lower()


def test_upload_forbidden_user(test_client, test_db, test_user, override_current_user):
    another_user = User(
        user_id=str(uuid.uuid4()),
        firstname="Other",
        lastname="User",
        username="otheruser",
        email="other@example.com",
        password="hashedpassword"
    )
    test_db.add(another_user)
    test_db.commit()

    file_content = io.BytesIO(b"fake_image_content")
    response = test_client.post(
        f"/posts/{another_user.user_id}",
        files={"file": ("public/11443b78e403ca36720b6f60fc66e90d.jpg", file_content, "image/png")}
    )

    assert response.status_code == 403, response.text
    assert "not allowed" in response.json()["detail"].lower()
