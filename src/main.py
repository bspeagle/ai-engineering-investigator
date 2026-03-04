from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from src.api import webhook_router
from src.utils import setup_logging
from src.config import settings

setup_logging()

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="AI Engineering Investigator",
    description="AI-powered GitLab issue triage and diagnostic system",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(webhook_router)


@app.get("/")
async def root():
    return {
        "service": "AI Engineering Investigator",
        "status": "running",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True
    )
