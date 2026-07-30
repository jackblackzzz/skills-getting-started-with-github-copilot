import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange (fixture): capture original participants and restore after each test
    original = {k: v['participants'][:] for k, v in activities.items()}
    yield
    for k in activities:
        activities[k]['participants'] = original[k][:]


def test_get_activities():
    # Arrange: TestClient and app are provided above

    # Act
    res = client.get('/activities')

    # Assert
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    assert 'Chess Club' in data


def test_signup_and_duplicates():
    # Arrange
    activity = 'Basketball Team' if 'Basketball Team' in activities else 'Chess Club'
    email = 'tester@example.com'
    if email in activities[activity]['participants']:
        activities[activity]['participants'].remove(email)

    # Act: first signup
    res = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert: signup succeeded and participant was added
    assert res.status_code == 200
    assert email in activities[activity]['participants']

    # Act: duplicate signup
    res2 = client.post(f"/activities/{activity}/signup?email={email}")

    # Assert: duplicate rejected
    assert res2.status_code == 400


def test_remove_participant():
    # Arrange
    activity = 'Basketball Team' if 'Basketball Team' in activities else 'Chess Club'
    email = 'remover@example.com'
    if email not in activities[activity]['participants']:
        activities[activity]['participants'].append(email)

    # Act
    res = client.delete(f"/activities/{activity}/participants?email={email}")

    # Assert
    assert res.status_code == 200
    assert email not in activities[activity]['participants']
