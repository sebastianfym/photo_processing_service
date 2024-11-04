import pytest

@pytest.mark.asyncio
async def test_crud_image(client):
    data = {
        "username": "Test",
        "password": "Test"
    }
    response = await client.post("/auth/login", json=data)
    assert response.status_code == 200
    access_token = response.json["access_token"]

    with open("tests/image/test_image.jpg", "rb") as file:
        response = client.post(
            "/image/upload_image",
            files={"file": ("test_image.jpg", file, "image/jpg")}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = client.post(
            "/image/upload_image",
            files={"file": ("test_image.png", file, "image/jpg")},
            headers=headers
        )
        assert response.status_code == 200
        assert len(response.json()) != 0

    image_id = response.json()[0]["id"]
    response = await client.get(f"/image/{image_id}")
    assert response.status_code == 200
    assert response.json()["id"] == image_id

    updated_data = {
        "title": "Updated title",
    }
    response = await client.patch(f"/image/{image_id}", json=updated_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

    response = await client.patch(f"/image/{image_id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Item"

    response = await client.delete(f"/image/{image_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

    response = await client.delete(f"/image/{image_id}", headers=headers)
    assert response.status_code == 200
