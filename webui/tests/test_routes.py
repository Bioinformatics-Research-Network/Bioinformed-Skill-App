from flask_dance.consumer.storage import MemoryStorage
from app import create_app
from app.auth import github_blueprint

def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<h1>BRN Skill Assessments</h1>" in response.data

