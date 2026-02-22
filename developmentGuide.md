# Development Guide

## Project Overview

AI agent server for developer portfolio site. Embeds portfolio content and returns relevant responses via LLM.

### Current Phase
Basic LLM integration with system prompts and guardrails (no RAG).

### Future Phase
RAG pipeline with Langchain and vector database.

---

## Tech Stack

| Category | Technology | Version |
|----------|------------|---------|
| Backend | FastAPI | 0.100+ |
| Validation | Pydantic | 2.x |
| LLM | Ollama (llama3) | - |
| Future: RAG | Langchain | - |
| Future: Vector DB | ChromaDB or FAISS | - |
| Testing | pytest | - |
| Linter | Ruff | - |
| Formatter | Black | - |

---

## Architecture

```
Client Request
    |
    v
Router (chat.py)
    |
    v
Usecase Layer (orchestration)
    |
    +---> Intent Resolver    # Identify intent (project/profile/skills)
    +---> Context Loader     # Load relevant context
    +---> Prompt Builder     # Build prompt with context
    |
    v
LLM Service (Ollama)
    |
    v
Response Validator (Guardrails)
    |
    v
Client Response
```

### Key Design Decisions

1. **Router contains no business logic** - Only request/response handling
2. **Service layer abstraction** - LLM service interface allows future Langchain swap
3. **Dependency injection** - Use FastAPI's `Depends()` for testability

---

## Project Structure

```
AI_Minimal_Agent/
├── app/
│   ├── main.py                 # FastAPI app + middleware
│   ├── routers/
│   │   └── chat.py             # API endpoints (no logic)
│   ├── schemas/
│   │   ├── request.py          # Request models
│   │   └── response.py         # Response models
│   ├── services/
│   │   ├── llm_service.py      # LLM abstraction
│   │   ├── prompt_builder.py   # Prompt construction
│   │   ├── intent_resolver.py  # Intent identification (project/profile/skills)
│   │   └── context_loader.py   # Context loading
│   ├── core/
│   │   ├── config.py           # Settings (pydantic-settings)
│   │   ├── guardrails.py       # Input/output validation
│   │   ├── security.py         # Security middleware
│   │   └── logging.py          # Structured logging
│   ├── middleware/
│   │   ├── rate_limiter.py     # Rate limiting
│   │   ├── request_id.py       # Request tracing
│   │   └── error_handler.py    # Global exception handling
│   └── data/
│       └── projects.json       # Project data
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── memory-bank/                # Agent context (see below)
├── docs/                       # Human documentation
├── CLAUDE.md                   # Claude Code entry point
├── .cursorrules                # Cursor entry point
└── developmentGuide.md         # This file
```

---

## Coding Standards

### Python Style
- **Formatter**: Black (line length 88)
- **Linter**: Ruff
- **Type hints**: Required for all functions

### FastAPI Rules

#### Routers: No Business Logic
```python
# Good
@router.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    return await chat_usecase(request)

# Bad
@router.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    project = resolve_project(request.message)  # Logic in router
    context = load_context(project)
    ...
```

#### Pydantic Validation
```python
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)

    model_config = ConfigDict(str_strip_whitespace=True)
```

#### Dependency Injection
```python
@router.post("/chat")
async def chat(
    request: ChatRequest,
    settings: Settings = Depends(get_settings),
    llm: LLMService = Depends(get_llm_service),
) -> ChatResponse:
    ...
```

#### Async First
```python
# Good - async for I/O operations
async def call_llm(prompt: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(...)

# Bad - blocking call in async context
def call_llm(prompt: str) -> str:
    response = requests.post(...)
```

### Naming Conventions

| Target | Convention | Example |
|--------|------------|---------|
| File | snake_case | `llm_service.py` |
| Class | PascalCase | `ChatRequest` |
| Function | snake_case | `resolve_project` |
| Constant | UPPER_SNAKE | `MAX_TOKENS` |
| Private | _prefix | `_validate_input` |

### Error Handling
```python
# Define custom exceptions
class ProjectNotFoundError(Exception):
    pass

# Use in service layer
def resolve_project(message: str) -> Project:
    project = find_project(message)
    if not project:
        raise ProjectNotFoundError(f"No project found for: {message}")
    return project

# Handle in global exception handler
@app.exception_handler(ProjectNotFoundError)
async def handle_project_not_found(request: Request, exc: ProjectNotFoundError):
    return JSONResponse(
        status_code=404,
        content={"error": "project_not_found", "message": str(exc)}
    )
```

---

## Documentation Standards

### General Principles
- No emojis in agent-facing documents
- Pure markdown syntax only
- Clear section headers
- Code examples with good/bad comparisons
- Explicit file path references (`app/services/llm_service.py`)

### Instruction Altitude
Write at the right level of specificity:

| Level | Characteristic | Example |
|-------|----------------|---------|
| Too Abstract | Agent interprets freely | "Use best practices" |
| Right Level | Clear constraints | "Use Pydantic for validation, return JSON with error/message keys" |
| Too Specific | Wastes tokens | "All functions must have exactly 3 parameters" |

---

## Security Principles

- Never commit secrets (.env, API keys, credentials)
- Validate all external input (Pydantic + guardrails)
- Sanitize LLM output before returning to client
- Log security events, never log sensitive data

Implementation details: see `app/core/security.py`, `app/core/guardrails.py`

---

## Testing Guide

### Commands
```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# With coverage
pytest --cov=app --cov-report=html

# Specific test
pytest tests/unit/test_intent_resolver.py -v
```

### Test Structure
```python
# tests/unit/test_intent_resolver.py

def test_resolve_intent_for_project():
    result = resolve_intent("Tell me about ClipPro")
    assert result.type == "project"
    assert result.target == "ClipPro"

def test_resolve_intent_for_profile():
    result = resolve_intent("What's your tech stack?")
    assert result.type == "profile"
```

### Fixtures
```python
# tests/conftest.py

@pytest.fixture
def mock_llm_service():
    service = Mock(spec=LLMService)
    service.generate.return_value = "Mocked response"
    return service
```

---

## Development Process

### Workflow
```
1. Requirement
      ↓
2. Agent Review
   - Codebase analysis
   - Web search (if needed)
   - Feasibility check
      ↓
3. Discussion → Epic Creation
   - docs/epic/[epic-name]/EPIC.md
      ↓
4. Phase Breakdown
   - Each phase = one commit
   - Another agent reviews and implements
      ↓
5. Implementation (TDD)
   - Write failing tests first
   - Implement to pass tests
   - Refactor if needed
      ↓
6. Commit
```

### Test-Driven Development
Each phase follows the TDD cycle:

```
1. Red   - Write failing test for the requirement
2. Green - Write minimal code to pass
3. Refactor - Clean up while keeping tests green
```

Rules:
- No production code without a failing test
- Write only enough test to fail
- Write only enough code to pass

### Epic Structure
```
docs/epic/[epic-name]/
├── EPIC.md           # Overview, goals, scope
└── phase-N.md        # Phase details
```

### Phase Document Template
```markdown
# Phase N: [Title]

## Scope
- What this phase covers

## Commit
type: subject

body (optional)

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

### Commit Convention
Follow [Conventional Commits](https://www.conventionalcommits.org/):

| Type | Description |
|------|-------------|
| feat | New feature |
| fix | Bug fix |
| refactor | Code change that neither fixes nor adds |
| docs | Documentation only |
| test | Adding or updating tests |
| chore | Build, config, tooling changes |

Format:
```
<type>: <subject>

[optional body]

[optional footer]
```

Examples:
```
feat: add LLM service abstraction layer

refactor: extract prompt building logic to separate module

fix: handle empty response from Ollama
```

---

## Agent Workflow

### Session Start
1. Read `developmentGuide.md`
2. Read `memory-bank/activeContext.md`
3. Read `memory-bank/systemPatterns.md` if architectural work

### Session End
Propose updates to:
- `memory-bank/activeContext.md`: Current state, next steps
- `memory-bank/progress.md`: Completed items, discovered issues

### Rule of Three
Add a new rule to this guide only when the same mistake occurs 3+ times.

---

## Common Mistakes

### 1. Ollama Not Running
- **Problem**: LLM service connection fails
- **Solution**: Run `ollama serve`, verify model is downloaded

### 2. Missing .env
- **Problem**: App uses default values
- **Solution**: Copy `.env.example` to `.env`, fill values

### 3. Blocking Calls in Async
- **Problem**: Using `requests` instead of `httpx` in async functions
- **Solution**: Use `httpx.AsyncClient` for HTTP calls

### 4. Business Logic in Router
- **Problem**: Router functions become hard to test
- **Solution**: Move logic to service/usecase layer

---

## References
- [memory-bank/](memory-bank/) - Agent context files
- [docs/](docs/) - Human documentation (epics, backlog)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)

---
Version: 2.0
Last Updated: 2026-02-20
