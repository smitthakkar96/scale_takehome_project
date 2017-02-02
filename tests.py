import pytest
import json

from app import app

@pytest.fixture
def client(request):
    return app.test_client()

def test_server_status(client):
    rv = client.get('/')
    assert (rv.status_code == 200)
    assert (json.loads(rv.data.decode())["response"] == "app is running perfectly fine"), "Error! server is not running"

def test_create_task_invalid_params(client):
    payload = {}
    rv = client.post('/api/tasks', data=json.dumps(payload), content_type="application/json")
    assert (rv.status_code == 400)

def test_create_task_invalid_urgency(client):
    payload = {
        "urgency" : "asap",
        "instruction" : "2 mins",
        "params" : {},
        "type" : "data_collection"
    }
    rv = client.post('/api/tasks', data=json.dumps(payload), content_type="application/json")
    assert (rv.status_code == 400)
    assert (json.loads(rv.data.decode())["response"] == "invalid urgency"), "invalid urgency test fails"

def test_create_task_invalid_type(client):
    payload = {
        "urgency" : "hour",
        "instruction" : "2 mins",
        "params" : {"key" : "value"},
        "type" : "don't know"
    }
    rv = client.post('/api/tasks', data=json.dumps(payload), content_type="application/json")
    assert (rv.status_code == 400)
    assert (json.loads(rv.data.decode())["response"] == "invalid type"), "invalid type test fails"

def test_create_task_invalid_params(client):
    payload = {
        "urgency" : "hour",
        "instruction" : "2 mins",
        "params" : {"key" : "value"},
        "type" : "data_collection"
    }
    rv = client.post('/api/tasks', data=json.dumps(payload), content_type="application/json")
    assert (rv.status_code == 400)
    assert (json.loads(rv.data.decode())["response"] == "attachment is required"), "invalid params test fails"

def test_create_task_success(client):
    payload = {
        "params" : {
            "fields": {
            "hiring_page": "Hiring Page URL"
            },
            "attachment": "http://www.scaleapi.com/",
        },
        "urgency": "day",
        "instruction": "Find the URL for the hiring page for the company with attached website.",
        "type": "data_collection",
    }
    rv = client.post('/api/tasks', data=json.dumps(payload), content_type="application/json")
    assert (rv.status_code == 200)
    assert ("taskId" in json.loads(rv.data.decode())["response"]), "invalid params test fails"

def test_complete_task(client):
    payload = {
        "params" : {
            "fields": {
            "hiring_page": "Hiring Page URL"
            },
            "attachment": "http://www.scaleapi.com/",
        },
        "urgency": "day",
        "instruction": "Find the URL for the hiring page for the company with attached website.",
        "type": "data_collection",
    }
    rv = client.post('/api/tasks', data=json.dumps(payload), content_type="application/json")
    taskId = json.loads(rv.data.decode())["response"]["taskId"]
    rv = client.put('/api/tasks/{}?status={}'.format(taskId, "finished"))
    assert (rv.status_code == 200)
    assert (json.loads(rv.data.decode())["response"]["status"] == "finished")

def test_cancel_task(client):
    payload = {
        "params" : {
            "fields": {
            "hiring_page": "Hiring Page URL"
            },
            "attachment": "http://www.scaleapi.com/",
        },
        "urgency": "day",
        "instruction": "Find the URL for the hiring page for the company with attached website.",
        "type": "data_collection",
    }
    rv = client.post('/api/tasks', data=json.dumps(payload), content_type="application/json")
    taskId = json.loads(rv.data.decode())["response"]["taskId"]
    rv = client.put('/api/tasks/{}?status={}'.format(taskId, "cancelled"))
    assert (rv.status_code == 200)
    assert (json.loads(rv.data.decode())["response"]["status"] == "cancelled")

def test_get_task_invalid_scaler(client):
    rv = client.get('/api/tasks/{}'.format("58922s2eabf8a81b5c23bff16f8"))
    assert (rv.status_code == 400)

def test_get_tasks(client):
    rv = client.get('/api/tasks/{}'.format("5892eabf8a81b5c23bff16f8"))
    assert (rv.status_code == 200)
    assert isinstance(json.loads(rv.data.decode())["response"]["tasks"], list)

def test_unassign_tasks(client):
    rv = client.post('/api/tasks/unassign/{}'.format("5892eabf8a81b5c23bff16f8"))
    assert (rv.status_code == 200)
    assert isinstance(json.loads(rv.data.decode())["response"]["tasks"], list)
