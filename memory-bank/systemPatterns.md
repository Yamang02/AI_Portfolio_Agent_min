# System Patterns

## Architecture Overview
Layered architecture with clear separation of concerns:
- Router: HTTP handling only
- Usecase: Orchestration
- Services: Business logic
- Core: Cross-cutting concerns

## Key Technical Decisions

### Decision 1: FastAPI + Pydantic
- Context: Need async web framework with strong validation
- Decision: FastAPI with Pydantic 2.x
- Rationale: Native async, automatic OpenAPI docs, Langchain compatible

### Decision 2: Service Layer Abstraction
- Context: Will swap Ollama direct calls for Langchain later
- Decision: Abstract LLM behind interface
- Rationale: Allows implementation swap without changing consumers

### Decision 3: Intent Resolver Pattern
- Context: Need to handle multiple content types (project/profile/skills)
- Decision: Intent Resolver identifies query type, Context Loader fetches data
- Rationale: Extensible for new content types without modifying resolver logic

## Design Patterns in Use
- Dependency Injection (FastAPI Depends)
- Repository Pattern (Context Loader)
- Strategy Pattern (LLM Service abstraction)

## Constraints
- Local LLM only (Ollama) in current phase
- No persistent storage for conversations
- Single-tenant design

---
Last Updated: 2026-02-20
