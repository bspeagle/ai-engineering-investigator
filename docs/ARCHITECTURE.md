# 🏗️ Architecture Documentation

> **For AI Agents:** This document explains the system architecture, design decisions, and component interactions. Use this to understand the codebase structure before making changes.

## System Overview

AI Engineering Investigator is a **webhook-driven AI analysis system** that:
1. Receives GitLab issue creation events
2. Detects issue type (bug or enhancement) from labels
3. Analyzes repository code and historical context
4. Generates adaptive reports using AI reasoning (diagnostics for bugs, implementation guidance for enhancements)
5. Posts results back to GitLab issues

## Architecture Layers

### 1. API Layer (`src/api/`)

**Purpose:** Handle external communication

**Components:**
- `webhook.py` - GitLab webhook endpoint with token validation
  - Validates webhook signatures
  - Filters event types (issues only)
  - Triggers background processing

**Design Pattern:** FastAPI with background tasks

**Key Decisions:**
- Background tasks prevent timeout on webhook response
- Token validation prevents unauthorized access
- Event filtering reduces unnecessary processing

### 2. Service Layer (`src/services/`)

**Purpose:** Core business logic

**Components:**

#### `orchestrator.py`
- **Role:** Coordinates entire analysis workflow
- **Pattern:** Async function with sequential steps
- **Dependencies:** All other services
- **Flow:**
  1. Clone/update repository
  2. Index code files
  3. Search for relevant context
  4. Generate AI diagnostic
  5. Post to GitLab

#### `repo_analyzer.py`
- **Role:** Git operations and code extraction
- **Pattern:** Class-based service
- **Key Methods:**
  - `get_or_clone_repo()` - Smart clone/pull
  - `get_code_files()` - Extract code with size limits
  - `get_recent_commits()` - Fetch commit history

#### `vector_store.py`
- **Role:** Semantic search using ChromaDB
- **Pattern:** Singleton-like client
- **Collections:**
  - `code_files` - Source code embeddings
  - `historical_issues` - Past issue embeddings
- **Key Feature:** Automatic embedding generation

#### `openai_client.py`
- **Role:** AI reasoning and report generation
- **Pattern:** Structured JSON output
- **Key Methods:**
  - `_build_prompt()` - Context-aware prompt engineering
  - `generate_diagnostic_report()` - AI analysis with fallback

#### `gitlab_client.py`
- **Role:** GitLab API operations
- **Pattern:** Authenticated API wrapper
- **Key Methods:**
  - `get_project_clone_url()` - Generate auth URL
  - `get_historical_issues()` - Fetch closed issues
  - `post_comment()` - Add diagnostic to issue

#### `report_generator.py`
- **Role:** Format AI output as Markdown
- **Pattern:** Static utility class
- **Output:** Structured, emoji-enhanced reports

### 3. Data Layer (`src/models/`)

**Purpose:** Data validation and type safety

**Components:**
- `schemas.py` - Pydantic models for:
  - `GitLabIssueEvent` - Webhook payload
  - `DiagnosticReport` - AI output structure
  - `ContextPayload` - Analysis input
  - `RelevantFile` - Code file metadata

**Design Pattern:** Pydantic for validation

### 4. Configuration (`src/config.py`)

**Purpose:** Environment-based configuration

**Pattern:** Pydantic Settings with `.env` support

**Key Decisions:**
- All settings configurable via environment variables
- Type validation on startup
- Fail-fast on missing required configs

## Data Flow

```
GitLab Webhook Event
  ↓
[webhook.py] Validate & Parse
  ↓
[orchestrator.py] Background Task
  ↓
[repo_analyzer.py] Clone Repository
  ↓
[vector_store.py] Index Code Files
  ↓
[vector_store.py] Search Relevant Context
  ↓
[gitlab_client.py] Fetch Historical Issues
  ↓
[openai_client.py] Detect Issue Type (bug/enhancement)
  ↓
[openai_client.py] Generate AI Analysis (adaptive prompt)
  ↓
[report_generator.py] Format as Markdown (adaptive template)
  ↓
[gitlab_client.py] Post to Issue
```

## Key Design Decisions

### 1. **Background Task Processing**
**Why:** Webhook responses must be fast (<30s). Analysis takes 30-60s.
**How:** FastAPI BackgroundTasks queues work asynchronously.

### 2. **Vector Search with ChromaDB**
**Why:** Semantic search finds relevant code without exact keyword matches.
**How:** Automatic embeddings on file content, similarity threshold filtering.

### 3. **Structured JSON Output from AI**
**Why:** Deterministic parsing, type-safe results, consistent format.
**How:** OpenAI's `response_format={"type": "json_object"}` parameter.

### 4. **File Size Limits**
**Why:** Prevent OOM errors, control token usage, focus on relevant code.
**How:** Configurable `MAX_FILE_SIZE_KB` and `MAX_CONTEXT_FILES`.

### 5. **Everything Configurable**
**Why:** Different repos have different needs, easy tuning without code changes.
**How:** Pydantic Settings with `.env` file.

## Component Dependencies

```
main.py
  └── webhook.py
        └── orchestrator.py
              ├── repo_analyzer.py
              ├── vector_store.py
              ├── openai_client.py
              ├── gitlab_client.py
              └── report_generator.py
```

## Extension Points

### Adding New Language Support
**File:** `src/services/repo_analyzer.py`
**Method:** Add extensions to `code_extensions` set in `get_code_files()`

### Changing AI Model
**File:** `.env`
**Variable:** `OPENAI_MODEL=gpt-4o` (or `gpt-4-turbo`, `o1`, etc.)

### Adding New Vector Collections
**File:** `src/services/vector_store.py`
**Method:** Add collection in `__init__()`, implement search methods

### Custom Report Sections
**File:** `src/services/report_generator.py`
**Method:** Extend `generate_markdown_report()` with new sections

## Error Handling Strategy

1. **Webhook Layer:** Return errors as HTTP status codes
2. **Service Layer:** Catch exceptions, log errors, continue processing
3. **AI Layer:** Fallback to generic report on API failures
4. **GitLab Layer:** Retry on network errors, log on final failure

## Testing Strategy

### Unit Tests
- Mock external dependencies (OpenAI, GitLab, Git)
- Test individual service methods
- Verify data model validation

### Integration Tests
- Test service interactions
- Use test fixtures for consistent data
- Mock only external APIs

### Coverage Goals
- Minimum: 70%
- Target: 85%
- Critical paths: 100%

## Performance Considerations

### Bottlenecks
1. **Git clone** - First run only, subsequent runs use pull
2. **Vector indexing** - O(n) on code files, cached in ChromaDB
3. **AI API calls** - 5-20s response time, no optimization possible

### Optimizations
- Clone/pull only when needed
- Index files once, reuse embeddings
- Limit context size to reduce API costs
- Background processing prevents timeout

## Security Considerations

1. **Webhook Validation:** HMAC token verification
2. **API Keys:** Environment variables only, never committed
3. **Git Credentials:** Temporary auth URLs, no persistent storage
4. **Input Validation:** Pydantic models validate all inputs
5. **File Access:** Limited to configured directory, no path traversal

## Monitoring & Observability

### Logging
- Structured logging to stdout
- Configurable log level via `LOG_LEVEL`
- Request/response tracing

### Health Checks
- `/webhook/health` - Service availability
- Docker healthcheck - Container monitoring

### Metrics to Track (Future)
- Issue processing time
- AI confidence scores
- Error rates by service
- Vector search accuracy

---

**For AI Agents Making Changes:**
1. Always check this document first
2. Maintain architectural patterns
3. Update this doc when adding major features
4. Keep service boundaries clear
5. Follow existing error handling patterns
