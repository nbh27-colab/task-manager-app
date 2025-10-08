import requests


def test_classify():
    res = requests.post("http://localhost:8000/ai/classify", json={
        "task_id": "test001",
        "description": "Viết báo cáo tài chính quý 3"
    })
    assert res.status_code == 200
    assert "category" in res.json()


def test_estimate():
    res = requests.post("http://localhost:8000/ai/estimate-time", json={
        "task_id": "test001",
        "description": "Viết báo cáo tài chính quý 3"
    })
    assert res.status_code == 200
    assert "estimated_minutes" in res.json()