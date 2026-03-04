import hmac
import hashlib
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.config import settings
from src.models import GitLabIssueEvent
from src.utils import get_logger
from src.services.orchestrator import process_issue

router = APIRouter(prefix="/webhook", tags=["webhook"])
logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)


def verify_gitlab_token(request: Request, payload: bytes) -> bool:
    token = request.headers.get("X-Gitlab-Token")
    if not token:
        return False
    return hmac.compare_digest(token, settings.gitlab_webhook_secret)


@router.post("/gitlab")
@limiter.limit("10/minute")
async def gitlab_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
):
    body = await request.body()
    
    if not verify_gitlab_token(request, body):
        logger.warning("Invalid webhook token received")
        raise HTTPException(status_code=401, detail="Invalid webhook token")
    
    try:
        event = GitLabIssueEvent.model_validate_json(body)
        
        if event.object_kind != "issue":
            logger.info(f"Ignoring non-issue event: {event.object_kind}")
            return {"status": "ignored", "reason": "not an issue event"}
        
        issue_action = event.object_attributes.get("action")
        if issue_action not in ["open", "reopen"]:
            logger.info(f"Ignoring issue action: {issue_action}")
            return {"status": "ignored", "reason": f"action is {issue_action}"}
        
        logger.info(f"Processing issue #{event.object_attributes.get('iid')}")
        
        background_tasks.add_task(
            process_issue,
            project_id=event.project.get("id"),
            issue_iid=event.object_attributes.get("iid"),
            issue_title=event.object_attributes.get("title"),
            issue_description=event.object_attributes.get("description", ""),
            issue_labels=event.object_attributes.get("labels", []),
        )
        
        return {"status": "accepted", "message": "Issue processing started"}
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def health_check():
    return {"status": "healthy"}
