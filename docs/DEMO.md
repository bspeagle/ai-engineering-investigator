# 🎯 Demo Guide - AI Engineering Investigator

## Quick Demo Setup

### Prerequisites
- GitLab.com account
- OpenAI API key
- Python 3.11+ or Docker

### Step 1: Initial Setup

```bash
# Clone and setup
git clone <repo-url>
cd AI_Engineering_Investigator
chmod +x setup.sh
./setup.sh
```

### Step 2: Configure Environment

Edit `.env` file with your credentials:

```bash
# Required
OPENAI_API_KEY=sk-your-key-here
GITLAB_TOKEN=glpat-your-token-here
GITLAB_WEBHOOK_SECRET=your-random-secret
GITLAB_PROJECT_ID=your-project-id

# Optional (defaults are fine)
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.3
```

### Step 3: Get GitLab Project ID

1. Go to your GitLab project
2. Look in Settings → General
3. Copy the Project ID number

### Step 4: Create GitLab Personal Access Token

1. GitLab → Preferences → Access Tokens
2. Create token with scopes:
   - `api`
   - `read_repository`
3. Copy token to `.env` as `GITLAB_TOKEN`

### Step 5: Start the Service

**Option A: Local Python**
```bash
source venv/bin/activate
python src/main.py
```

**Option B: Docker**
```bash
docker-compose up -d
docker-compose logs -f
```

Service will be running at `http://localhost:8000`

### Step 6: Expose Service (for GitLab webhooks)

**For Demo Purposes:**

Use ngrok or similar to expose localhost:
```bash
ngrok http 8000
```

Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)

### Step 7: Configure GitLab Webhook

1. Go to your GitLab project
2. Settings → Webhooks
3. Add webhook:
   - **URL:** `https://your-ngrok-url.ngrok.io/webhook/gitlab`
   - **Secret Token:** (same as `GITLAB_WEBHOOK_SECRET` in .env)
   - **Trigger:** Check "Issues events"
   - **SSL verification:** Enable (ngrok supports SSL)
4. Click "Add webhook"
5. Test it with "Test → Issues events"

### Step 8: Create a Test Issue

1. Go to your GitLab project
2. Issues → New Issue
3. Create an issue like:
   ```
   Title: Login endpoint returning 401 errors
   
   Description:
   Users are reporting they can't log in. The /api/auth/login endpoint
   is returning 401 errors even with correct credentials. This started
   happening after yesterday's deployment.
   ```
4. Submit the issue

### Step 9: Watch the Magic

Within 30-60 seconds, the AI diagnostic report will appear as a comment on the issue!

## What to Show in Demo

### 1. The Setup
- Show the simple configuration (just API keys needed)
- Highlight Docker support for easy deployment

### 2. The Workflow
- Create a realistic issue in GitLab
- Show the webhook triggering
- Display the comprehensive diagnostic report

### 3. The Report Contents
- **Root Cause Analysis** - AI's reasoning
- **Relevant Files** - Semantic search found the right code
- **Historical Context** - Similar past issues
- **Reproduction Steps** - Actionable guidance
- **Fix Strategy** - Engineering-level suggestions
- **Blast Radius** - Impact assessment
- **Confidence Score** - Transparency in AI reasoning

### 4. The Value Proposition
- **Time Saved:** Hours of investigation → Automated in seconds
- **Knowledge Capture:** Historical context preserved
- **Consistency:** Every issue gets Staff Engineer-level triage
- **Onboarding:** New team members get context immediately

## Demo Tips

### Best Repos to Demo With
- Medium-sized codebases (not too simple, not too complex)
- Projects with some closed issues (for historical context)
- Code with clear structure (easier for AI to analyze)

### Sample Issue Scenarios

**Bug Report:**
```
Title: Database connection pool exhausted
Description: Application crashes after ~1000 requests. 
Error logs show "Too many connections" from PostgreSQL.
```

**Performance Issue:**
```
Title: API response times degraded 10x
Description: /api/users endpoint taking 5+ seconds to respond.
Started after adding user profile images feature.
```

**Feature Request:**
```
Title: Add rate limiting to public API
Description: Need to prevent abuse of public endpoints.
Should support per-IP and per-API-key limits.
```

## Troubleshooting Demo Issues

### Webhook Not Triggering
- Check ngrok is running: `curl http://localhost:4040/api/tunnels`
- Verify webhook URL in GitLab
- Check secret token matches
- Review GitLab webhook delivery logs

### No Report Posted
- Check application logs: `docker-compose logs -f`
- Verify OpenAI API key is valid
- Check GitLab token has correct permissions
- Ensure network access to OpenAI and GitLab

### Report Quality Issues
- Increase `MAX_CONTEXT_FILES` for more code context
- Adjust `SIMILARITY_THRESHOLD` (lower = more results)
- Try `OPENAI_MODEL=gpt-4-turbo` for deeper analysis
- Add more historical issues for better context

## Advanced Demo Features

### Show Configurability
Open `.env.example` and highlight all the tunable parameters

### Show Containerization
```bash
docker-compose ps
docker-compose logs --tail=20
```

### Show Health Monitoring
```bash
curl http://localhost:8000/webhook/health
```

### Show the Architecture
Display the mermaid diagram from README.md

## Demo Script Outline

1. **Problem Statement** (1 min)
   - Engineers spend hours triaging issues
   - Knowledge silos when people leave
   - Inconsistent investigation quality

2. **Solution Overview** (2 min)
   - Show architecture diagram
   - Explain AI-powered analysis
   - Highlight GitLab integration

3. **Live Demo** (5 min)
   - Create issue in GitLab
   - Show webhook trigger
   - Display comprehensive report
   - Walk through report sections

4. **Value Proposition** (2 min)
   - Time savings calculation
   - Team velocity improvement
   - Knowledge preservation

5. **Technical Deep Dive** (optional)
   - Show code structure
   - Explain vector search
   - Demonstrate configurability

---

**Ready to win this hackathon! 🏴‍☠️**
