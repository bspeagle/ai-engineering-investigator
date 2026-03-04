import pytest
from src.services.report_generator import ReportGenerator
from src.models import AnalysisReport, RelevantFile


def test_generate_markdown_report_basic(sample_diagnostic_report):
    report = ReportGenerator.generate_markdown_report(
        sample_diagnostic_report,
        "Test Issue Title"
    )
    
    assert "# 🔍 AI Bug Analysis Report" in report
    assert "Test Issue Title" in report
    assert "Database connection pool exhausted" in report
    assert "85%" in report


def test_generate_markdown_report_with_relevant_files():
    report_data = AnalysisReport(
        issue_type="bug",
        core_analysis="Test cause",
        relevant_files=[
            RelevantFile(
                file_path="src/test.py",
                reason="Contains the bug",
                snippet="def test():\n    pass"
            )
        ],
        related_issues=[],
        suggested_reproduction_steps=["Step 1"],
        recommended_approach="Fix it",
        impact_assessment="Low",
        confidence=0.9,
        confidence_reason="Very confident"
    )
    
    report = ReportGenerator.generate_markdown_report(report_data, "Test")
    
    assert "src/test.py" in report
    assert "Contains the bug" in report
    assert "def test():" in report


def test_generate_markdown_report_with_related_issues():
    report_data = AnalysisReport(
        issue_type="bug",
        core_analysis="Test",
        relevant_files=[],
        related_issues=["#123", "#456"],
        suggested_reproduction_steps=[],
        recommended_approach="Test",
        impact_assessment="Low",
        confidence=0.8,
        confidence_reason="Test"
    )
    
    report = ReportGenerator.generate_markdown_report(report_data, "Test")
    
    assert "#123" in report
    assert "#456" in report
    assert "Related Historical Issues" in report


def test_generate_markdown_report_with_reproduction_steps():
    report_data = AnalysisReport(
        issue_type="bug",
        core_analysis="Test",
        relevant_files=[],
        related_issues=[],
        suggested_reproduction_steps=[
            "First step",
            "Second step",
            "Third step"
        ],
        recommended_approach="Test",
        impact_assessment="Low",
        confidence=0.8,
        confidence_reason="Test"
    )
    
    report = ReportGenerator.generate_markdown_report(report_data, "Test")
    
    assert "1. First step" in report
    assert "2. Second step" in report
    assert "3. Third step" in report


def test_report_includes_all_sections(sample_diagnostic_report):
    report = ReportGenerator.generate_markdown_report(
        sample_diagnostic_report,
        "Test Issue"
    )
    
    assert "Root Cause Analysis" in report
    assert "Relevant Files" in report
    assert "Related Historical Issues" in report
    assert "Reproduction Steps" in report
    assert "Recommended Fix Strategy" in report
    assert "Blast Radius" in report
    assert "Confidence Assessment" in report
    assert "AI Engineering Investigator" in report
