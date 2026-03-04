import json
from typing import Dict
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.config import settings
from src.models import AnalysisReport, ContextPayload
from src.utils import get_logger

logger = get_logger(__name__)


class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        before_sleep=lambda retry_state: logger.warning(
            f"OpenAI API call failed, retrying... (attempt {retry_state.attempt_number})"
        )
    )
    def generate_diagnostic_report(self, context: ContextPayload) -> AnalysisReport:
        issue_type = self._detect_issue_type(context.issue_labels)
        prompt = self._build_prompt(context, issue_type)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior software engineer performing issue analysis. Analyze the provided context and generate a structured report for bugs or feature enhancements."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=settings.openai_temperature,
                max_tokens=settings.openai_max_tokens,
                response_format={"type": "json_object"}
            )
            
            response_text = response.choices[0].message.content
            logger.info("Received diagnostic response from OpenAI")
            
            report_data = json.loads(response_text)
            return AnalysisReport(**report_data)
            
        except Exception as e:
            logger.error(f"Error generating diagnostic report: {e}")
            return self._create_fallback_report(str(e))
    
    def _detect_issue_type(self, labels: list) -> str:
        enhancement_keywords = {'enhancement', 'feature', 'improvement', 'feature request'}
        bug_keywords = {'bug', 'defect', 'issue', 'error', 'fix'}
        
        labels_lower = [label.lower() for label in labels]
        
        if any(keyword in labels_lower for keyword in enhancement_keywords):
            return 'enhancement'
        elif any(keyword in labels_lower for keyword in bug_keywords):
            return 'bug'
        
        return 'bug'
    
    def _build_prompt(self, context: ContextPayload, issue_type: str) -> str:
        prompt_parts = [
            "# Issue Analysis Request",
            "",
            "## New Issue",
            f"**Title:** {context.issue_title}",
            f"**Description:**\n{context.issue_description}",
            f"**Labels:** {', '.join(context.issue_labels) if context.issue_labels else 'None'}",
            "",
            "## Repository Context",
        ]
        
        if context.repository_structure:
            prompt_parts.extend([
                "### Repository Structure",
                "```",
                context.repository_structure[:settings.prompt_repo_structure_max_chars],
                "```",
                ""
            ])
        
        if context.relevant_code_files:
            prompt_parts.append("### Relevant Code Files")
            for i, file_data in enumerate(context.relevant_code_files[:5]):
                prompt_parts.extend([
                    f"\n**File {i+1}: {file_data.get('path', 'unknown')}**",
                    f"Similarity: {file_data.get('similarity', 0):.2f}",
                    "```",
                    file_data.get('content', '')[:settings.prompt_file_content_max_chars],
                    "```",
                    ""
                ])
        
        if context.historical_issues:
            prompt_parts.append("### Similar Historical Issues")
            for issue in context.historical_issues[:5]:
                prompt_parts.append(f"- #{issue.get('issue_id')}: {issue.get('title')} (similarity: {issue.get('similarity', 0):.2f})")
            prompt_parts.append("")
        
        if context.recent_commits:
            prompt_parts.append("### Recent Commits")
            for commit in context.recent_commits[:5]:
                prompt_parts.append(f"- {commit.get('sha')}: {commit.get('message')} ({commit.get('files_changed')} files)")
            prompt_parts.append("")
        
        if issue_type == 'enhancement':
            prompt_parts.extend([
                "",
                "## Analysis Instructions",
                "This is a FEATURE/ENHANCEMENT request. Provide:",
                "- Requirements analysis",
                "- Implementation recommendations",
                "- Technical approach",
                "- Effort estimation",
                "",
                "## Required Output",
                "Generate a JSON response with the following structure:",
                "```json",
                "{",
                '  "issue_type": "enhancement",',
                '  "core_analysis": "What is being requested and why it\'s needed",',
                '  "relevant_files": [',
                '    {"file_path": "path/to/file", "reason": "why this file needs changes", "snippet": "optional code snippet"}',
                '  ],',
                '  "related_issues": ["#123", "#456"],',
                '  "suggested_reproduction_steps": [],',
                '  "recommended_approach": "Detailed implementation strategy and architecture",',
                '  "implementation_details": "Technical specifics: dependencies, database changes, API modifications, etc.",',
                '  "effort_estimate": "Low/Medium/High with justification",',
                '  "impact_assessment": "Scope and affected components",',
                '  "confidence": 0.85,',
                '  "confidence_reason": "Explanation of confidence level"',
                "}",
                "```"
            ])
        else:
            prompt_parts.extend([
                "",
                "## Analysis Instructions",
                "This is a BUG report. Provide:",
                "- Root cause analysis",
                "- Reproduction steps",
                "- Fix strategy",
                "- Impact assessment",
                "",
                "## Required Output",
                "Generate a JSON response with the following structure:",
                "```json",
                "{",
                '  "issue_type": "bug",',
                '  "core_analysis": "Detailed analysis of the root cause",',
                '  "relevant_files": [',
                '    {"file_path": "path/to/file", "reason": "why this file is relevant", "snippet": "optional code snippet"}',
                '  ],',
                '  "related_issues": ["#123", "#456"],',
                '  "suggested_reproduction_steps": ["step 1", "step 2"],',
                '  "recommended_approach": "Detailed fix strategy",',
                '  "implementation_details": null,',
                '  "effort_estimate": null,',
                '  "impact_assessment": "Blast radius (low/medium/high with explanation)",',
                '  "confidence": 0.85,',
                '  "confidence_reason": "Explanation of confidence level"',
                "}",
                "```"
            ])
        
        prompt_parts.extend([
            "",
            "Analyze thoroughly and provide actionable insights."
        ])
        
        return "\n".join(prompt_parts)
    
    def _create_fallback_report(self, error_msg: str) -> AnalysisReport:
        return AnalysisReport(
            issue_type="bug",
            core_analysis=f"Unable to generate analysis report: {error_msg}",
            relevant_files=[],
            related_issues=[],
            suggested_reproduction_steps=["Manual investigation required"],
            recommended_approach="Unable to determine - manual analysis needed",
            implementation_details=None,
            effort_estimate=None,
            impact_assessment="Unknown",
            confidence=0.0,
            confidence_reason="Analysis failed due to error"
        )
