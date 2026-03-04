import pytest
from unittest.mock import patch, MagicMock
from src.services.openai_client import OpenAIClient
from src.models import ContextPayload


@patch("src.services.openai_client.OpenAI")
def test_openai_client_initialization(mock_openai):
    client = OpenAIClient()
    assert client.model == "gpt-4o"
    mock_openai.assert_called_once()


@patch("src.services.openai_client.OpenAI")
def test_build_prompt_basic(mock_openai):
    client = OpenAIClient()
    
    context = ContextPayload(
        issue_title="Login broken",
        issue_description="Users can't log in",
        issue_labels=["bug"]
    )
    
    prompt = client._build_prompt(context, 'bug')
    
    assert "Login broken" in prompt
    assert "Users can't log in" in prompt
    assert "bug" in prompt
    assert "JSON" in prompt


@patch("src.services.openai_client.OpenAI")
def test_build_prompt_with_code_files(mock_openai):
    client = OpenAIClient()
    
    context = ContextPayload(
        issue_title="Test",
        issue_description="Test",
        relevant_code_files=[
            {
                "path": "src/auth.py",
                "content": "def login(): pass",
                "similarity": 0.95
            }
        ]
    )
    
    prompt = client._build_prompt(context, 'bug')
    
    assert "src/auth.py" in prompt
    assert "0.95" in prompt
    assert "def login():" in prompt


@patch("src.services.openai_client.OpenAI")
def test_build_prompt_with_historical_issues(mock_openai):
    client = OpenAIClient()
    
    context = ContextPayload(
        issue_title="Test",
        issue_description="Test",
        historical_issues=[
            {"issue_id": "123", "title": "Similar bug", "similarity": 0.88}
        ]
    )
    
    prompt = client._build_prompt(context, 'bug')
    
    assert "#123" in prompt
    assert "Similar bug" in prompt
    assert "0.88" in prompt


@patch("src.services.openai_client.OpenAI")
def test_build_prompt_with_commits(mock_openai):
    client = OpenAIClient()
    
    context = ContextPayload(
        issue_title="Test",
        issue_description="Test",
        recent_commits=[
            {
                "sha": "abc1234",
                "message": "Fix auth",
                "files_changed": 3
            }
        ]
    )
    
    prompt = client._build_prompt(context, 'bug')
    
    assert "abc1234" in prompt
    assert "Fix auth" in prompt
    assert "3 files" in prompt


@patch("src.services.openai_client.OpenAI")
def test_generate_diagnostic_report_success(mock_openai, mock_openai_client):
    mock_openai.return_value = mock_openai_client
    
    client = OpenAIClient()
    context = ContextPayload(
        issue_title="Test",
        issue_description="Test"
    )
    
    report = client.generate_diagnostic_report(context)
    
    assert report.core_analysis == "test"
    assert report.confidence == 0.8
    assert mock_openai_client.chat.completions.create.called


@patch("src.services.openai_client.OpenAI")
def test_generate_diagnostic_report_handles_error(mock_openai):
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    mock_openai.return_value = mock_client
    
    client = OpenAIClient()
    context = ContextPayload(
        issue_title="Test",
        issue_description="Test"
    )
    
    report = client.generate_diagnostic_report(context)
    
    assert report.confidence == 0.0
    assert "Unable to generate" in report.core_analysis
    assert "API Error" in report.core_analysis
