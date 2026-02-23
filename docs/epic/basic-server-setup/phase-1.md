# Phase 1: Project Structure & Configuration

## Scope

- 디렉토리 구조 생성 및 `__init__.py` 초기화
- `app/core/config.py` - pydantic-settings 기반 중앙화 설정
- `requirements.txt` 업데이트
- `.env.example` 업데이트

## Commit

chore: initialize project structure and configuration

## Acceptance Criteria

- [ ] `app/routers/`, `app/schemas/`, `app/services/`, `app/core/`, `app/middleware/` 디렉토리 존재
- [ ] `tests/unit/`, `tests/integration/` 디렉토리 존재
- [ ] `app/core/config.py`에서 환경변수를 pydantic-settings로 읽음
- [ ] `requirements.txt`에 httpx, pydantic-settings, pytest, pytest-asyncio 포함

## Status

- ✅ Completed

## Notes

- Project directories and initial files created; `app/core/config.py` uses pydantic-settings. `requirements.txt` updated and test scaffolding added.

Last Updated: 2026-02-23
