import pytest
from unittest.mock import patch, MagicMock
from src.services.openai_client import OpenAIClient
from src.models import AnalysisReport, ContextPayload


@patch("src.services.openai_client.OpenAI")
def test_detect_issue_type_bug(mock_openai):
    client = OpenAIClient()
    
    assert client._detect_issue_type(['bug']) == 'bug'
    assert client._detect_issue_type(['defect']) == 'bug'
    assert client._detect_issue_type(['error', 'critical']) == 'bug'
    assert client._detect_issue_type(['BUG']) == 'bug'


@patch("src.services.openai_client.OpenAI")
def test_detect_issue_type_enhancement(mock_openai):
    client = OpenAIClient()
    
    assert client._detect_issue_type(['enhancement']) == 'enhancement'
    assert client._detect_issue_type(['feature']) == 'enhancement'
    assert client._detect_issue_type(['improvement']) == 'enhancement'
    assert client._detect_issue_type(['feature request']) == 'enhancement'
    assert client._detect_issue_type(['ENHANCEMENT']) == 'enhancement'


@patch("src.services.openai_client.OpenAI")
def test_detect_issue_type_default_to_bug(mock_openai):
    client = OpenAIClient()
    
    assert client._detect_issue_type([]) == 'bug'
    assert client._detect_issue_type(['documentation']) == 'bug'
    assert client._detect_issue_type(['question']) == 'bug'


@patch("src.services.openai_client.OpenAI")
def test_build_prompt_bug(mock_openai):
    client = OpenAIClient()
    
    context = ContextPayload(
        issue_title="Login fails",
        issue_description="Users can't log in",
        issue_labels=["bug"]
    )
    
    prompt = client._build_prompt(context, 'bug')
    
    assert "BUG report" in prompt
    assert "Root cause analysis" in prompt
    assert "Reproduction steps" in prompt
    assert "Fix strategy" in prompt
    assert '"issue_type": "bug"' in prompt
    assert "impact_assessment" in prompt.lower()


@patch("src.services.openai_client.OpenAI")
def test_build_prompt_enhancement(mock_openai):
    client = OpenAIClient()
    
    context = ContextPayload(
        issue_title="Add dark mode",
        issue_description="Users want dark mode support",
        issue_labels=["enhancement"]
    )
    
    prompt = client._build_prompt(context, 'enhancement')
    
    assert "FEATURE/ENHANCEMENT request" in prompt
    assert "Requirements analysis" in prompt
    assert "Implementation recommendations" in prompt
    assert "Effort estimation" in prompt
    assert '"issue_type": "enhancement"' in prompt
    assert "implementation_details" in prompt
    assert "effort_estimate" in prompt


@patch("src.services.openai_client.OpenAI")
def test_generate_report_detects_enhancement(mock_openai, mock_openai_client):
    mock_response = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content='{"issue_type": "enhancement", "core_analysis": "test", "relevant_files": [], "related_issues": [], "suggested_reproduction_steps": [], "recommended_approach": "test", "implementation_details": "details", "effort_estimate": "Medium", "impact_assessment": "test", "confidence": 0.8, "confidence_reason": "test"}'
                )
            )
        ]
    )
    mock_openai_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_openai_client
    
    client = OpenAIClient()
    context = ContextPayload(
        issue_title="Add feature",
        issue_description="New feature",
        issue_labels=["enhancement"]
    )
    
    report = client.generate_diagnostic_report(context)
    
    assert report.issue_type == "enhancement"
    assert report.implementation_details == "details"
    assert report.effort_estimate == "Medium"


@patch("src.services.openai_client.OpenAI")
def test_generate_report_detects_bug(mock_openai, mock_openai_client):
    mock_response = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content='{"issue_type": "bug", "core_analysis": "root cause", "relevant_files": [], "related_issues": [], "suggested_reproduction_steps": ["step1"], "recommended_approach": "fix", "implementation_details": null, "effort_estimate": null, "impact_assessment": "low", "confidence": 0.9, "confidence_reason": "test"}'
                )
            )
        ]
    )
    mock_openai_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_openai_client
    
    client = OpenAIClient()
    context = ContextPayload(
        issue_title="Login broken",
        issue_description="Bug description",
        issue_labels=["bug"]
    )
    
    report = client.generate_diagnostic_report(context)
    
    assert report.issue_type == "bug"
    assert len(report.suggested_reproduction_steps) > 0
    assert report.implementation_details is None
    assert report.effort_estimate is None
