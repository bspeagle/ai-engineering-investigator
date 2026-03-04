import pytest
from unittest.mock import MagicMock
import os

# Set test environment variables BEFORE any imports that load settings
os.environ.setdefault("OPENAI_API_KEY", "test-openai-key")
os.environ.setdefault("GITLAB_TOKEN", "test-gitlab-token")
os.environ.setdefault("GITLAB_WEBHOOK_SECRET", "test-webhook-secret")
os.environ.setdefault("GITLAB_PROJECT_ID", "12345")


@pytest.fixture
def mock_settings():
    from src.config import Settings
    return Settings(
        openai_api_key="test-key",
        gitlab_token="test-token",
        gitlab_webhook_secret="test-secret",
        gitlab_project_id="12345",
        gitlab_url="https://gitlab.com",
        app_host="0.0.0.0",
        app_port=8000,
        log_level="INFO",
        openai_model="gpt-4o",
        openai_temperature=0.3,
        openai_max_tokens=4000,
        chroma_persist_dir="./test_data/chroma",
        embedding_model="text-embedding-3-small",
        repo_clone_dir="./test_data/repos",
        max_file_size_kb=500,
        max_context_files=15,
        code_snippet_max_lines=50,
        max_historical_issues=10,
        max_recent_commits=10,
        similarity_threshold=0.7,
        webhook_verify_ssl=True,
        webhook_timeout_seconds=30
    )


@pytest.fixture
def sample_issue_event():
    return {
        "object_kind": "issue",
        "project": {
            "id": 12345,
            "name": "test-project"
        },
        "object_attributes": {
            "iid": 1,
            "title": "Test issue",
            "description": "Test description",
            "action": "open",
            "labels": ["bug"]
        },
        "user": {
            "name": "Test User"
        }
    }


@pytest.fixture
def sample_diagnostic_report():
    from src.models import AnalysisReport, RelevantFile
    return AnalysisReport(
        issue_type="bug",
        core_analysis="Database connection pool exhausted",
        relevant_files=[
            RelevantFile(
                file_path="src/database/connection.py",
                reason="Manages connection pool configuration"
            )
        ],
        related_issues=["#123"],
        suggested_reproduction_steps=[
            "Deploy to production",
            "Generate 1000+ concurrent requests"
        ],
        recommended_approach="Increase max_connections in config",
        implementation_details=None,
        effort_estimate=None,
        impact_assessment="Medium - affects all database operations",
        confidence=0.85,
        confidence_reason="Similar issue resolved in #123"
    )


@pytest.fixture
def mock_openai_client():
    mock = MagicMock()
    mock.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content='{"issue_type": "bug", "core_analysis": "test", "relevant_files": [], "related_issues": [], "suggested_reproduction_steps": [], "recommended_approach": "test", "implementation_details": null, "effort_estimate": null, "impact_assessment": "low", "confidence": 0.8, "confidence_reason": "test"}'
                )
            )
        ]
    )
    return mock


@pytest.fixture
def mock_gitlab_client():
    mock = MagicMock()
    mock.get_project.return_value = MagicMock(
        http_url_to_repo="https://gitlab.com/test/repo.git"
    )
    return mock
