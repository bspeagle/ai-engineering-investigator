import gitlab
from typing import List, Dict, Optional
from src.config import settings
from src.utils import get_logger

logger = get_logger(__name__)


class GitLabClient:
    def __init__(self):
        self.gl = gitlab.Gitlab(settings.gitlab_url, private_token=settings.gitlab_token)
        self.gl.auth()
    
    def get_project(self, project_id: int):
        try:
            return self.gl.projects.get(project_id)
        except Exception as e:
            logger.error(f"Error fetching project {project_id}: {e}")
            raise
    
    def get_project_clone_url(self, project_id: int) -> str:
        project = self.get_project(project_id)
        http_url = project.http_url_to_repo
        
        authenticated_url = http_url.replace(
            'https://',
            f'https://oauth2:{settings.gitlab_token}@'
        )
        
        return authenticated_url
    
    def get_historical_issues(self, project_id: int, max_issues: int = None) -> List[Dict]:
        if max_issues is None:
            max_issues = settings.max_historical_issues * 2
        
        try:
            project = self.get_project(project_id)
            issues = project.issues.list(state='closed', per_page=max_issues)
            
            historical_data = []
            for issue in issues:
                historical_data.append({
                    'iid': issue.iid,
                    'title': issue.title,
                    'description': issue.description or '',
                    'state': issue.state,
                    'labels': issue.labels
                })
            
            logger.info(f"Retrieved {len(historical_data)} historical issues")
            return historical_data
        except Exception as e:
            logger.error(f"Error fetching historical issues: {e}")
            return []
    
    def post_comment(self, project_id: int, issue_iid: int, comment: str) -> bool:
        try:
            project = self.get_project(project_id)
            issue = project.issues.get(issue_iid)
            issue.notes.create({'body': comment})
            logger.info(f"Posted comment to issue #{issue_iid}")
            return True
        except Exception as e:
            logger.error(f"Error posting comment: {e}")
            return False
    
    def get_issue_details(self, project_id: int, issue_iid: int) -> Optional[Dict]:
        try:
            project = self.get_project(project_id)
            issue = project.issues.get(issue_iid)
            
            return {
                'iid': issue.iid,
                'title': issue.title,
                'description': issue.description or '',
                'labels': issue.labels,
                'state': issue.state,
                'author': issue.author.get('name', 'Unknown')
            }
        except Exception as e:
            logger.error(f"Error fetching issue details: {e}")
            return None
