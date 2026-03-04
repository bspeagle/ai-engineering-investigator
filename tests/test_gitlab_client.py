import pytest
from unittest.mock import MagicMock, patch
from src.services.gitlab_client import GitLabClient


@pytest.fixture
def mock_gitlab():
    with patch('src.services.gitlab_client.gitlab.Gitlab') as mock:
        yield mock


@pytest.fixture
def gitlab_client(mock_gitlab):
    return GitLabClient()


def test_gitlab_client_initialization(mock_gitlab):
    client = GitLabClient()
    assert client.gl is not None
    mock_gitlab.assert_called_once()


def test_get_project(gitlab_client, mock_gitlab):
    mock_project = MagicMock()
    mock_project.id = 12345
    mock_gitlab.return_value.projects.get.return_value = mock_project
    
    project = gitlab_client.get_project("12345")
    
    assert project.id == 12345
    mock_gitlab.return_value.projects.get.assert_called_once_with("12345")


def test_get_project_clone_url(gitlab_client, mock_gitlab):
    mock_project = MagicMock()
    mock_project.http_url_to_repo = "https://gitlab.com/user/repo.git"
    mock_gitlab.return_value.projects.get.return_value = mock_project
    
    url = gitlab_client.get_project_clone_url("12345")
    
    assert "test-gitlab-token" in url
    assert "gitlab.com" in url
    assert "user/repo.git" in url


def test_get_historical_issues(gitlab_client, mock_gitlab):
    mock_project = MagicMock()
    mock_issue1 = MagicMock()
    mock_issue1.iid = 1
    mock_issue1.title = "Bug 1"
    mock_issue1.description = "Description 1"
    mock_issue1.state = "closed"
    mock_issue1.labels = ["bug"]
    
    mock_issue2 = MagicMock()
    mock_issue2.iid = 2
    mock_issue2.title = "Bug 2"
    mock_issue2.description = "Description 2"
    mock_issue2.state = "closed"
    mock_issue2.labels = ["feature"]
    
    mock_project.issues.list.return_value = [mock_issue1, mock_issue2]
    mock_gitlab.return_value.projects.get.return_value = mock_project
    
    issues = gitlab_client.get_historical_issues("12345", max_issues=5)
    
    assert len(issues) == 2
    assert issues[0]["iid"] == 1
    assert issues[0]["title"] == "Bug 1"
    assert issues[1]["iid"] == 2


def test_get_historical_issues_with_limit(gitlab_client, mock_gitlab):
    mock_project = MagicMock()
    mock_issues = []
    for i in range(5):
        issue = MagicMock()
        issue.iid = i
        issue.title = f"Issue {i}"
        issue.description = "desc"
        issue.state = "closed"
        issue.labels = []
        mock_issues.append(issue)
    
    mock_project.issues.list.return_value = mock_issues
    mock_gitlab.return_value.projects.get.return_value = mock_project
    
    issues = gitlab_client.get_historical_issues("12345", max_issues=5)
    
    assert len(issues) == 5


def test_post_comment(gitlab_client, mock_gitlab):
    mock_project = MagicMock()
    mock_issue = MagicMock()
    mock_project.issues.get.return_value = mock_issue
    mock_gitlab.return_value.projects.get.return_value = mock_project
    
    gitlab_client.post_comment("12345", 1, "Test comment")
    
    mock_issue.notes.create.assert_called_once_with({"body": "Test comment"})


def test_get_issue_details(gitlab_client, mock_gitlab):
    mock_project = MagicMock()
    mock_issue = MagicMock()
    mock_issue.iid = 1
    mock_issue.title = "Test Issue"
    mock_issue.description = "Test Description"
    mock_issue.labels = ["bug", "critical"]
    mock_issue.state = "open"
    
    mock_project.issues.get.return_value = mock_issue
    mock_gitlab.return_value.projects.get.return_value = mock_project
    
    issue = gitlab_client.get_issue_details("12345", 1)
    
    assert issue["iid"] == 1
    assert issue["title"] == "Test Issue"
    assert issue["description"] == "Test Description"
    assert issue["labels"] == ["bug", "critical"]


def test_get_project_handles_error(gitlab_client, mock_gitlab):
    mock_gitlab.return_value.projects.get.side_effect = Exception("API Error")
    
    with pytest.raises(Exception):
        gitlab_client.get_project("12345")


def test_get_historical_issues_handles_error(gitlab_client, mock_gitlab):
    mock_gitlab.return_value.projects.get.side_effect = Exception("API Error")
    
    issues = gitlab_client.get_historical_issues("12345", max_issues=5)
    
    assert issues == []


def test_post_comment_handles_error(gitlab_client, mock_gitlab):
    mock_project = MagicMock()
    mock_project.issues.get.side_effect = Exception("API Error")
    mock_gitlab.return_value.projects.get.return_value = mock_project
    
    # Should not raise, just log error
    gitlab_client.post_comment("12345", 1, "Test comment")
