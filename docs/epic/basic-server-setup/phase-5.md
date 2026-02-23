# Phase 5: Middleware

## Scope

- `app/middleware/request_id.py` - UUID 기반 요청 추적
- `app/middleware/rate_limiter.py` - 인메모리 슬라이딩 윈도우 Rate Limiting
- `app/middleware/error_handler.py` - 전역 예외 핸들러
- `tests/unit/test_rate_limiter.py`

## Commit

feat: add security middleware (rate limiting, request ID, error handler)

## Acceptance Criteria

- [ ] 모든 요청에 `X-Request-ID` 헤더 포함 (요청/응답 모두)
- [ ] IP별 분당 요청 수 제한 (`RATE_LIMIT_RPM` 기본값 60)
- [ ] Rate limit 초과 시 429 응답 + `Retry-After` 헤더
- [ ] `LLMServiceError` → 503 응답
- [ ] 예상치 못한 예외 → 500 응답
- [ ] 에러 응답 형식: `{"error": ..., "message": ..., "request_id": ...}`
- [ ] 테스트 모두 통과

## Status

- ✅ Completed

## Notes

- Implemented `RequestIDMiddleware`, in-memory sliding-window `RateLimiterMiddleware`, and standardized error handling behavior. Rate limiting and middleware unit tests passing.

Last Updated: 2026-02-23
