# AI Engineering Investigator

## AI-Powered GitLab Issue Intelligence Engine

------------------------------------------------------------------------

# 1. Idea Description

AI Engineering Investigator is an intelligent issue triage system that
integrates directly with GitLab. When a new issue is created, the system
automatically analyzes the issue against the entire repository,
historical issues, recent commits, and related code to generate a
structured diagnostic report.

Instead of engineers spending hours reproducing issues, searching
through the codebase, reviewing prior tickets, and tracing recent
changes, this system performs that initial investigative work
automatically.

The output is a structured, senior-level engineering diagnostic report
posted directly into the GitLab issue. It includes:

-   Likely root cause analysis
-   Relevant files and functions
-   Related historical issues and commits
-   Suggested reproduction steps
-   Proposed fix strategy
-   Estimated blast radius
-   Confidence score with reasoning

The system does not automatically modify code or create merge requests.
It serves as an AI-powered Staff Engineer assistant that reduces triage
time, improves developer velocity, and prevents knowledge silos.

This solution is designed to be practical, deployable, and immediately
valuable within real engineering workflows.

------------------------------------------------------------------------

# 2. Solution Overview

The AI Engineering Investigator operates as an event-driven service
triggered by GitLab webhooks.

When a new issue is created (or labeled for investigation), the system
performs the following steps:

1.  Retrieves the issue title, description, labels, and metadata.
2.  Pulls a snapshot of the repository.
3.  Performs semantic search across the codebase to identify relevant
    files.
4.  Searches historical issues using embeddings to identify similar past
    problems.
5.  Retrieves recent commits affecting related files.
6.  Constructs a structured context payload.
7.  Sends the payload to OpenAI GPT-4o for deep reasoning.
8.  Receives structured JSON output.
9.  Renders a clean, structured Markdown diagnostic report.
10. Posts the report back to the GitLab issue via API.

The result is an automated, intelligent triage report that mirrors the
reasoning process of a senior engineer.

------------------------------------------------------------------------

# 3. Technical Overview

## Architecture

GitLab Webhook\
↓\
FastAPI Service\
↓\
Context Builder\
↓\
Embedding & Semantic Search Layer\
↓\
OpenAI GPT-4o (Structured JSON Prompt)\
↓\
Markdown Report Generator\
↓\
GitLab API Comment

------------------------------------------------------------------------

## Core Components

### 1. Webhook Listener

-   Built with FastAPI
-   Receives issue creation events
-   Filters based on project or label

### 2. Repository Context Extraction

-   Clone or pull repository snapshot
-   Extract file structure
-   Parse relevant modules

### 3. Semantic Search

-   Generate embeddings for codebase
-   Store in lightweight vector store (pgvector, Chroma, or SQLite)
-   Perform similarity search against issue content

### 4. Historical Intelligence

-   Embed past issues
-   Retrieve semantically similar issues
-   Pull related commit hashes

### 5. Context Structuring

Construct a structured JSON payload including: - Issue details - Top
relevant files - Related issues - Recent commits - Code snippets
(bounded size)

### 6. OpenAI Reasoning Layer

Use structured prompting to enforce deterministic JSON output schema:

Expected Output Schema:

{ "likely_root_cause": "...", "relevant_files": \[ { "file_path": "...",
"reason": "..." } \], "related_issues": \["#1234"\],
"suggested_reproduction_steps": \["..."\], "suggested_fix_strategy":
"...", "blast_radius": "...", "confidence": 0.0, "confidence_reason":
"..." }

### 7. Markdown Report Generator

Render output as:

## AI Diagnostic Report

### Likely Root Cause

...

### Relevant Files

-   path/to/file.py --- reason

### Related Historical Issues

-   #1234

### Suggested Reproduction Steps

1.  ...
2.  ...

### Suggested Fix Strategy

...

### Estimated Blast Radius

...

### Confidence Score

82% Reason: ...

------------------------------------------------------------------------

## Model Strategy

Primary Model: - OpenAI GPT-4o

Optional Upgrade: - OpenAI o1 for deeper architectural reasoning if
necessary

The system relies on structured prompting rather than complex
multi-agent orchestration. Deterministic schema enforcement ensures
predictable outputs.

------------------------------------------------------------------------

## Deployment Strategy

-   Containerized FastAPI service
-   GitLab project-level webhook configuration
-   Lightweight vector store (local or containerized)
-   Stateless processing per issue event

------------------------------------------------------------------------

## Why This Solution Wins

-   Reduces triage time
-   Improves engineering velocity
-   Captures institutional knowledge
-   Enhances onboarding
-   Practical and deployable immediately
-   Demonstrates meaningful AI integration in SDLC

------------------------------------------------------------------------

# End of Document
