# Project Brief

## Project Name
AI_Minimal_Agent

## Purpose
AI agent server for developer portfolio site that answers questions about portfolio content using LLM.

## Goals
- Provide conversational interface for portfolio exploration
- Return relevant, accurate responses about projects, skills, and profile
- Maintain extensible architecture for future RAG integration

## Scope

### In Scope
- Chat API endpoint for portfolio queries
- Intent resolution (project/profile/skills)
- LLM integration (Ollama)
- Input/output validation and guardrails
- Basic security (rate limiting, CORS, input sanitization)

### Out of Scope (Current Phase)
- RAG pipeline
- Vector database
- Multi-user support
- Authentication

## Success Criteria
- Server responds to portfolio-related queries accurately
- Clean separation between layers (router/service/core)
- Test coverage for core functionality
- Documentation for agent collaboration

---
Last Updated: 2026-02-20
