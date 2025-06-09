from src.tests.conftest import client


def test_retrieve_trip(client: client):
    response = client.get("/api/v1/trips/1")
    assert response.status_code == 200