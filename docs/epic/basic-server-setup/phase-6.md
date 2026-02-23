# Phase 6: Router & App Integration

## Scope

- `app/routers/chat.py` - 얇은 라우터 (비즈니스 로직 없음)
- `app/main.py` 재작성 - 미들웨어/라우터/CORS 등록
- `tests/integration/test_chat_api.py`

## Commit

feat: integrate router and configure FastAPI app with security

## Acceptance Criteria

- [ ] `app/routers/chat.py`에 비즈니스 로직 없음 (`Depends()` 사용)
- [ ] CORS: `ALLOWED_ORIGINS` 환경변수로 설정 가능
- [ ] `/health` 엔드포인트 정상 동작
- [ ] `/chat` 엔드포인트: guardrails 적용 → LLM 호출 → 응답 반환
- [ ] 잘못된 입력 → 422 응답
- [ ] Rate limit 초과 → 429 응답
- [ ] 통합 테스트 모두 통과 (mock LLM service 사용)

## Status

- ✅ Completed

## Notes

- Router implemented as a thin layer (`Depends()` used). FastAPI app (`app/main.py`) wired with CORS, middleware stack and chat router. Integration tests using mocked LLM service all passing.

Last Updated: 2026-02-23
