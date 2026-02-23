# Epic: Basic FastAPI LLM Server with Security

## Overview

현재 3개 파일로 구성된 최소 MVP를 `developmentGuide.md`에 명시된 레이어드 아키텍처로 리팩토링하고, 기본 보안을 갖춘 LLM 서버를 구축한다.

## Goals

- 레이어드 아키텍처 구조 확립 (Router / Service / Core / Middleware)
- 비동기 LLM 서비스 추상화 (향후 Langchain 교체 가능)
- 기본 보안: CORS, 인메모리 Rate Limiting, 입출력 가드레일
- 요청 추적: Request ID 미들웨어
- TDD 워크플로우에 따른 테스트 작성

## Out of Scope

- Intent Resolver, Context Loader, Prompt Builder (다음 에픽)
- RAG, 벡터 DB
- Redis 기반 Rate Limiting
- 인증/인가

## Phases

| Phase | Title | Commit Type |
|-------|-------|-------------|
| 1 | Project Structure & Configuration | chore |
| 2 | Schemas with Validation | feat |
| 3 | Async LLM Service Abstraction | feat |
| 4 | Guardrails & Logging | feat |
| 5 | Middleware (Rate Limit, Request ID, Error Handler) | feat |
| 6 | Router & App Integration | feat |

## Acceptance Criteria

- [ ] 모든 app/ 코드가 레이어드 아키텍처를 따름
- [ ] 모든 HTTP I/O가 async (httpx)로 처리됨
- [ ] Rate Limiting: IP별 분당 요청 제한 적용
- [ ] CORS: 환경변수로 허용 오리진 설정 가능
- [ ] 입력: 길이 제한, 공백 제거, 위험 패턴 필터링
- [ ] 출력: 응답 검증 후 클라이언트 전달
- [ ] 에러 응답 형식 일관성: `{"error": ..., "message": ..., "request_id": ...}`
- [ ] pytest 테스트 통과
