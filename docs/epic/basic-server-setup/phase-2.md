# Phase 2: Schemas with Validation

## Scope

- `app/schemas/request.py` - 입력 검증 포함 ChatRequest
- `app/schemas/response.py` - request_id 포함 ChatResponse
- `app/schemas/__init__.py` - 외부 노출 통합
- `tests/unit/test_schemas.py`

## Commit

feat: add validated request/response schemas

## Acceptance Criteria

- [ ] `ChatRequest.message`: min_length=1, max_length=1000, 공백 자동 제거
- [ ] `ChatResponse`: response, request_id 필드 포함
- [ ] 빈 문자열 입력 시 ValidationError 발생
- [ ] 1001자 입력 시 ValidationError 발생
- [ ] 테스트 모두 통과

## Status

- ✅ Completed

## Notes

- `ChatRequest` 및 `ChatResponse` 구현 완료. 입력/출력 검증 및 관련 단위 테스트 작성 및 통과.

Last Updated: 2026-02-23
