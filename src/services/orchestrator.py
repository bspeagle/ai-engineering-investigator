from typing import List
from src.services.repo_analyzer import RepositoryAnalyzer
from src.services.vector_store import VectorStore
from src.services.openai_client import OpenAIClient
from src.services.gitlab_client import GitLabClient
from src.services.report_generator import ReportGenerator
from src.models import ContextPayload
from src.utils import get_logger

logger = get_logger(__name__)


async def process_issue(
    project_id: int,
    issue_iid: int,
    issue_title: str,
    issue_description: str,
    issue_labels: List[str]
):
    try:
        logger.info(f"Starting processing for issue #{issue_iid} in project {project_id}")
        
        gitlab_client = GitLabClient()
        repo_analyzer = RepositoryAnalyzer()
        vector_store = VectorStore()
        openai_client = OpenAIClient()
        
        project_name = f"project_{project_id}"
        clone_url = gitlab_client.get_project_clone_url(project_id)
        
        logger.info("Cloning/updating repository")
        repo = repo_analyzer.get_or_clone_repo(clone_url, project_name)
        
        logger.info("Extracting repository context")
        code_files = repo_analyzer.get_code_files(repo)
        
        logger.info("Indexing code files in vector store")
        vector_store.index_code_files(code_files, project_id)
        
        logger.info("Searching for relevant code")
        query = f"{issue_title}\n{issue_description}"
        relevant_code = vector_store.search_relevant_code(query, project_id)
        
        logger.info("Fetching historical issues")
        historical_issues = gitlab_client.get_historical_issues(project_id)
        
        for hist_issue in historical_issues:
            vector_store.index_issue(
                issue_id=hist_issue['iid'],
                title=hist_issue['title'],
                description=hist_issue['description'],
                project_id=project_id
            )
        
        logger.info("Searching for similar historical issues")
        similar_issues = vector_store.search_similar_issues(query, project_id)
        
        logger.info("Getting recent commits")
        recent_commits = repo_analyzer.get_recent_commits(repo)
        
        logger.info("Extracting repository structure")
        repo_structure = repo_analyzer.extract_file_structure(repo)
        
        context = ContextPayload(
            issue_title=issue_title,
            issue_description=issue_description,
            issue_labels=issue_labels,
            relevant_code_files=relevant_code,
            historical_issues=similar_issues,
            recent_commits=recent_commits,
            repository_structure=repo_structure
        )
        
        logger.info("Generating AI diagnostic report")
        diagnostic_report = openai_client.generate_diagnostic_report(context)
        
        logger.info("Converting to markdown")
        markdown_report = ReportGenerator.generate_markdown_report(
            diagnostic_report,
            issue_title
        )
        
        logger.info("Posting report to GitLab issue")
        success = gitlab_client.post_comment(project_id, issue_iid, markdown_report)
        
        if success:
            logger.info(f"Successfully processed issue #{issue_iid}")
        else:
            logger.error(f"Failed to post comment for issue #{issue_iid}")
        
    except Exception as e:
        logger.error(f"Error processing issue #{issue_iid}: {e}", exc_info=True)
