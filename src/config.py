from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )
    
    openai_api_key: str
    gitlab_token: str
    gitlab_webhook_secret: str
    
    gitlab_url: str = "https://gitlab.com"
    gitlab_project_id: str
    
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.3
    openai_max_tokens: int = 4000
    
    chroma_persist_dir: str = "./data/chroma"
    embedding_model: str = "text-embedding-3-small"
    
    repo_clone_dir: str = "./data/repos"
    max_file_size_kb: int = 500
    max_context_files: int = 15
    code_snippet_max_lines: int = 50
    
    max_historical_issues: int = 10
    max_recent_commits: int = 10
    similarity_threshold: float = 0.7
    
    repo_structure_max_lines: int = 100
    prompt_repo_structure_max_chars: int = 500
    prompt_file_content_max_chars: int = 1000
    
    webhook_verify_ssl: bool = True
    webhook_timeout_seconds: int = 30


settings = Settings()
