import requests


def test_create_task():
    data = {
    "title": "Test Task",
    "description": "This is a test",
    "status": "todo",
    "due_date": "2025-10-10T12:00:00",
    "category_id": 1,
    "project_id": 1
    }
    res = requests.post("http://localhost:8000/tasks/", json=data)
    assert res.status_code == 200


def test_get_tasks():
    res = requests.get("http://localhost:8000/tasks/")
    assert res.status_code == 200
    assert isinstance(res.json(), list)

