import os
from pathlib import Path
from typing import List, Dict
import git
from src.config import settings
from src.utils import get_logger

logger = get_logger(__name__)


class RepositoryAnalyzer:
    def __init__(self):
        self.clone_dir = Path(settings.repo_clone_dir)
        self.clone_dir.mkdir(parents=True, exist_ok=True)
    
    def get_or_clone_repo(self, project_url: str, project_name: str) -> git.Repo:
        repo_path = self.clone_dir / project_name
        
        try:
            if repo_path.exists():
                logger.info(f"Repository exists, pulling latest: {project_name}")
                try:
                    repo = git.Repo(repo_path)
                    repo.remotes.origin.pull()
                    logger.info(f"Successfully pulled latest changes for {project_name}")
                except git.exc.GitCommandError as e:
                    logger.warning(f"Pull failed, repository may have conflicts: {e}")
                    logger.info("Using existing repository without pulling")
                    repo = git.Repo(repo_path)
            else:
                logger.info(f"Cloning repository: {project_name}")
                repo = git.Repo.clone_from(project_url, repo_path)
                logger.info(f"Successfully cloned {project_name}")
            
            return repo
        except git.exc.GitCommandError as e:
            logger.error(f"Git operation failed for {project_name}: {e}")
            raise RuntimeError(f"Failed to access repository: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error with repository {project_name}: {e}")
            raise
    
    def extract_file_structure(self, repo: git.Repo) -> str:
        repo_path = Path(repo.working_dir)
        structure_lines = []
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            level = root.replace(str(repo_path), '').count(os.sep)
            indent = '  ' * level
            folder_name = os.path.basename(root)
            if folder_name:
                structure_lines.append(f'{indent}{folder_name}/')
            
            sub_indent = '  ' * (level + 1)
            for file in files:
                if not file.startswith('.'):
                    structure_lines.append(f'{sub_indent}{file}')
        
        return '\n'.join(structure_lines[:settings.repo_structure_max_lines])
    
    def get_code_files(self, repo: git.Repo) -> List[Dict[str, str]]:
        repo_path = Path(repo.working_dir)
        code_files = []
        
        code_extensions = {
            '.py', '.js', '.ts', '.java', '.go', '.rb', '.php', '.cpp', '.c', '.h', '.rs',
            '.cs', '.vb', '.fs', '.cshtml', '.xaml'
        }
        
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in code_extensions:
                    try:
                        file_size_kb = file_path.stat().st_size / 1024
                        if file_size_kb > settings.max_file_size_kb:
                            continue
                        
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        relative_path = file_path.relative_to(repo_path)
                        code_files.append({
                            'path': str(relative_path),
                            'content': content,
                            'size_kb': round(file_size_kb, 2)
                        })
                    except Exception as e:
                        logger.warning(f"Could not read file {file_path}: {e}")
        
        return code_files
    
    def get_recent_commits(self, repo: git.Repo, max_commits: int = None) -> List[Dict[str, str]]:
        if max_commits is None:
            max_commits = settings.max_recent_commits
        
        commits = []
        for commit in list(repo.iter_commits())[:max_commits]:
            commits.append({
                'sha': commit.hexsha[:8],
                'message': commit.message.strip(),
                'author': str(commit.author),
                'date': commit.committed_datetime.isoformat(),
                'files_changed': len(commit.stats.files)
            })
        
        return commits
    
    def extract_code_snippet(self, file_path: str, repo: git.Repo, max_lines: int = None) -> str:
        if max_lines is None:
            max_lines = settings.code_snippet_max_lines
        
        full_path = Path(repo.working_dir) / file_path
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[:max_lines]
            return ''.join(lines)
        except Exception as e:
            logger.warning(f"Could not extract snippet from {file_path}: {e}")
            return ""
