import pytest

@pytest.mark.asyncio
async def test_user_action(client):
    data = {
        "username": "Test",
        "password": "Test"
    }

    response = await client.post("/auth/register", json=data)
    assert response.status_code == 201
    assert response.json()["msg"] == "User registered successfully"

    response = await client.post("/auth/register", json=data)
    assert response.status_code == 400
    assert response.json()["detail"] == "User already register"

    response = await client.post("/auth/login", json=data)
    assert response.status_code == 200

    refresh_token = response.json["refresh_token"]

    response = await client.post("/auth/refresh", json={"refresh_token": "refresh_token"})
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
