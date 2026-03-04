import pytest
from pydantic import ValidationError
from src.models import AnalysisReport, RelevantFile, ContextPayload, GitLabIssueEvent


def test_relevant_file_creation():
    file = RelevantFile(
        file_path="src/test.py",
        reason="Test reason"
    )
    assert file.file_path == "src/test.py"
    assert file.reason == "Test reason"
    assert file.snippet is None


def test_relevant_file_with_snippet():
    file = RelevantFile(
        file_path="src/test.py",
        reason="Test reason",
        snippet="def test(): pass"
    )
    assert file.snippet == "def test(): pass"


def test_diagnostic_report_creation(sample_diagnostic_report):
    assert sample_diagnostic_report.confidence == 0.85
    assert sample_diagnostic_report.impact_assessment == "Medium - affects all database operations"
    assert len(sample_diagnostic_report.relevant_files) == 1


def test_diagnostic_report_confidence_validation():
    with pytest.raises(ValidationError):
        AnalysisReport(
            issue_type="bug",
            core_analysis="Test",
            relevant_files=[],
            related_issues=[],
            suggested_reproduction_steps=[],
            recommended_approach="Test",
            impact_assessment="Low",
            confidence=1.5,
            confidence_reason="Test"
        )


def test_diagnostic_report_confidence_range():
    report = AnalysisReport(
        issue_type="bug",
        core_analysis="Test",
        relevant_files=[],
        related_issues=[],
        suggested_reproduction_steps=[],
        recommended_approach="Test",
        impact_assessment="Low",
        confidence=0.0,
        confidence_reason="Test"
    )
    assert report.confidence == 0.0
    
    report = AnalysisReport(
        issue_type="bug",
        core_analysis="Test",
        relevant_files=[],
        related_issues=[],
        suggested_reproduction_steps=[],
        recommended_approach="Test",
        impact_assessment="Low",
        confidence=1.0,
        confidence_reason="Test"
    )
    assert report.confidence == 1.0


def test_context_payload_creation():
    payload = ContextPayload(
        issue_title="Test Issue",
        issue_description="Test Description",
        issue_labels=["bug", "critical"],
        relevant_code_files=[{"path": "test.py", "content": "test"}],
        historical_issues=[{"iid": 1, "title": "Old issue"}],
        recent_commits=[{"sha": "abc123", "message": "Fix"}]
    )
    
    assert payload.issue_title == "Test Issue"
    assert len(payload.issue_labels) == 2
    assert payload.issue_labels[0] == "bug"


def test_context_payload_defaults():
    payload = ContextPayload(
        issue_title="Test",
        issue_description="Test"
    )
    
    assert payload.issue_labels == []
    assert payload.relevant_code_files == []
    assert payload.historical_issues == []
    assert payload.recent_commits == []
    assert payload.repository_structure is None


def test_gitlab_issue_event_parsing(sample_issue_event):
    event = GitLabIssueEvent(**sample_issue_event)
    
    assert event.object_kind == "issue"
    assert event.project["id"] == 12345
    assert event.object_attributes["title"] == "Test issue"
    assert event.user["name"] == "Test User"
