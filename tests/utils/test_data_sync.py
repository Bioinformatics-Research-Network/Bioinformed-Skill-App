def test_index(client):
    """
    Test that index page is accessible without login
    """
    response = client.get("/")
    assert response.status_code == 200
