import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/webhook/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "AI Engineering Investigator"
    assert data["status"] == "running"


@patch("src.api.webhook.verify_gitlab_token")
@patch("src.api.webhook.process_issue")
def test_webhook_valid_token(mock_process, mock_verify, sample_issue_event):
    mock_verify.return_value = True
    
    response = client.post(
        "/webhook/gitlab",
        json=sample_issue_event,
        headers={"X-Gitlab-Token": "test-secret"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    assert mock_process.called


@patch("src.api.webhook.verify_gitlab_token")
def test_webhook_invalid_token(mock_verify, sample_issue_event):
    mock_verify.return_value = False
    
    response = client.post(
        "/webhook/gitlab",
        json=sample_issue_event,
        headers={"X-Gitlab-Token": "wrong-secret"}
    )
    
    assert response.status_code == 401


@patch("src.api.webhook.verify_gitlab_token")
def test_webhook_ignores_non_issue_events(mock_verify):
    mock_verify.return_value = True
    
    event = {
        "object_kind": "merge_request",
        "project": {"id": 123},
        "object_attributes": {}
    }
    
    response = client.post(
        "/webhook/gitlab",
        json=event,
        headers={"X-Gitlab-Token": "test-secret"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "ignored"
    assert response.json()["reason"] == "not an issue event"


@patch("src.api.webhook.verify_gitlab_token")
def test_webhook_ignores_closed_issues(mock_verify):
    mock_verify.return_value = True
    
    event = {
        "object_kind": "issue",
        "project": {"id": 123},
        "object_attributes": {
            "action": "close",
            "iid": 1,
            "title": "Test"
        }
    }
    
    response = client.post(
        "/webhook/gitlab",
        json=event,
        headers={"X-Gitlab-Token": "test-secret"}
    )
    
    assert response.status_code == 200
    assert response.json()["status"] == "ignored"
