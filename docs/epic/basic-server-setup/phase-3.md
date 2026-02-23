# Phase 3: Async LLM Service Abstraction

## Scope

- `app/services/llm_service.py` - Protocol 인터페이스 + OllamaService 구현
- `tests/unit/test_llm_service.py`
- `tests/conftest.py` - mock fixture
- 기존 `app/llm.py` 제거

## Commit

feat: add async LLM service abstraction for Ollama

## Acceptance Criteria

- [ ] `LLMService` Protocol 정의 (generate 메서드)
- [ ] `OllamaService`: httpx.AsyncClient 사용, timeout 설정
- [ ] 연결 실패 시 `LLMServiceError` raise
- [ ] 타임아웃 시 `LLMServiceError` raise
- [ ] `get_llm_service()` 의존성 팩토리 존재
- [ ] 기존 `app/llm.py` 없음
- [ ] 테스트 모두 통과 (httpx mock 사용)

## Status

- ✅ Completed

## Notes

- Implemented `LLMService` Protocol and `OllamaService` (async httpx). Added `get_llm_service()` factory and removed legacy synchronous `app/llm.py`. Unit tests for service behave correctly using httpx mocks.

Last Updated: 2026-02-23
