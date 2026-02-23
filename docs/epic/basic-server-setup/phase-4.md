# Phase 4: Guardrails & Logging

## Scope

- `app/core/exceptions.py` - 커스텀 예외 클래스
- `app/core/guardrails.py` - 입출력 검증 및 필터링
- `app/core/logging.py` - 구조화 로깅
- `tests/unit/test_guardrails.py`

## Commit

feat: add guardrails for input/output validation and logging

## Acceptance Criteria

- [ ] `LLMServiceError`, `RateLimitError` 커스텀 예외 존재
- [ ] `validate_input()`: XSS/스크립트 패턴 필터링
- [ ] `validate_output()`: 빈 응답 처리
- [ ] 구조화 로깅 설정 (보안 이벤트 로거 포함)
- [ ] 테스트 모두 통과

## Status

- ✅ Completed

## Notes

- Added custom exceptions, `validate_input`/`validate_output` guardrails, and structured JSON logging with security event helper. Guardrails unit tests passing.

Last Updated: 2026-02-23
