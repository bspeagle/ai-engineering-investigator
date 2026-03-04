import pytest
from src.services.report_generator import ReportGenerator
from src.models import AnalysisReport, RelevantFile


def test_bug_report_format():
    report = AnalysisReport(
        issue_type="bug",
        core_analysis="Memory leak in connection pool",
        relevant_files=[
            RelevantFile(
                file_path="src/db/connection.py",
                reason="Manages connection lifecycle"
            )
        ],
        related_issues=["#123"],
        suggested_reproduction_steps=["Step 1", "Step 2"],
        recommended_approach="Fix connection cleanup",
        implementation_details=None,
        effort_estimate=None,
        impact_assessment="High - affects all DB operations",
        confidence=0.9,
        confidence_reason="Clear evidence"
    )
    
    markdown = ReportGenerator.generate_markdown_report(report, "DB Connection Issue")
    
    assert "🔍 AI Bug Analysis Report" in markdown
    assert "Root Cause Analysis" in markdown
    assert "Memory leak in connection pool" in markdown
    assert "Reproduction Steps" in markdown
    assert "Recommended Fix Strategy" in markdown
    assert "Blast Radius" in markdown
    assert "High - affects all DB operations" in markdown
    assert "Technical Implementation Details" not in markdown
    assert "Effort Estimate" not in markdown


def test_enhancement_report_format():
    report = AnalysisReport(
        issue_type="enhancement",
        core_analysis="Request for dark mode theme support",
        relevant_files=[
            RelevantFile(
                file_path="src/ui/theme.css",
                reason="Theme styles need dark mode variants"
            )
        ],
        related_issues=["#456"],
        suggested_reproduction_steps=[],
        recommended_approach="Implement CSS variables with theme switching",
        implementation_details="Add theme toggle, create dark color palette, update localStorage",
        effort_estimate="Medium - ~3-5 days of work",
        impact_assessment="UI components and styling system",
        confidence=0.85,
        confidence_reason="Standard implementation pattern"
    )
    
    markdown = ReportGenerator.generate_markdown_report(report, "Add Dark Mode")
    
    assert "💡 AI Feature Analysis Report" in markdown
    assert "Requirements Analysis" in markdown
    assert "Request for dark mode theme support" in markdown
    assert "Recommended Implementation Approach" in markdown
    assert "Technical Implementation Details" in markdown
    assert "Add theme toggle" in markdown
    assert "Effort Estimate" in markdown
    assert "Medium - ~3-5 days" in markdown
    assert "Scope & Impact" in markdown
    assert "UI components and styling system" in markdown
    assert "Reproduction Steps" not in markdown
    assert "Blast Radius" not in markdown


def test_enhancement_without_optional_fields():
    report = AnalysisReport(
        issue_type="enhancement",
        core_analysis="Add export feature",
        relevant_files=[],
        related_issues=[],
        suggested_reproduction_steps=[],
        recommended_approach="Add CSV export button",
        implementation_details=None,
        effort_estimate=None,
        impact_assessment="Export module only",
        confidence=0.7,
        confidence_reason="Straightforward addition"
    )
    
    markdown = ReportGenerator.generate_markdown_report(report, "Export Data")
    
    assert "💡 AI Feature Analysis Report" in markdown
    assert "Technical Implementation Details" not in markdown
    assert "Effort Estimate" not in markdown


def test_files_section_wording_differs():
    bug_report = AnalysisReport(
        issue_type="bug",
        core_analysis="Test",
        relevant_files=[RelevantFile(file_path="test.py", reason="test")],
        related_issues=[],
        suggested_reproduction_steps=[],
        recommended_approach="Test",
        impact_assessment="Test",
        confidence=0.8,
        confidence_reason="Test"
    )
    
    enhancement_report = AnalysisReport(
        issue_type="enhancement",
        core_analysis="Test",
        relevant_files=[RelevantFile(file_path="test.py", reason="test")],
        related_issues=[],
        suggested_reproduction_steps=[],
        recommended_approach="Test",
        impact_assessment="Test",
        confidence=0.8,
        confidence_reason="Test"
    )
    
    bug_markdown = ReportGenerator.generate_markdown_report(bug_report, "Bug")
    enhancement_markdown = ReportGenerator.generate_markdown_report(enhancement_report, "Feature")
    
    assert "Relevant Files" in bug_markdown
    assert "Files Requiring Changes" in enhancement_markdown
