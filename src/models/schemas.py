from pydantic import BaseModel, Field
from typing import List, Optional


class GitLabIssueEvent(BaseModel):
    object_kind: str
    project: dict
    object_attributes: dict
    user: Optional[dict] = None


class RelevantFile(BaseModel):
    file_path: str
    reason: str
    snippet: Optional[str] = None


class AnalysisReport(BaseModel):
    issue_type: str = Field(..., description="Type of issue: bug or enhancement")
    core_analysis: str = Field(..., description="Root cause for bugs, or requirement analysis for enhancements")
    relevant_files: List[RelevantFile] = Field(default_factory=list)
    related_issues: List[str] = Field(default_factory=list)
    suggested_reproduction_steps: List[str] = Field(default_factory=list, description="For bugs: steps to reproduce")
    recommended_approach: str = Field(..., description="Fix strategy for bugs, or implementation approach for enhancements")
    implementation_details: Optional[str] = Field(None, description="Technical details for enhancements")
    effort_estimate: Optional[str] = Field(None, description="Complexity assessment for enhancements")
    impact_assessment: str = Field(..., description="Blast radius for bugs, or scope for enhancements")
    confidence: float = Field(..., ge=0.0, le=1.0)
    confidence_reason: str


# Keep backwards compatibility alias
DiagnosticReport = AnalysisReport


class ContextPayload(BaseModel):
    issue_title: str
    issue_description: str
    issue_labels: List[str] = Field(default_factory=list)
    relevant_code_files: List[dict] = Field(default_factory=list)
    historical_issues: List[dict] = Field(default_factory=list)
    recent_commits: List[dict] = Field(default_factory=list)
    repository_structure: Optional[str] = None
