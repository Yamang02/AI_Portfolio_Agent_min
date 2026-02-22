# [EPIC] 기본 서버 구축

**우선순위**: P0
**상태**: 계획 중
**예상 시작**: 2026-02-20

---

## 목표

RAG 확장이 가능한 FastAPI 기본 구조 구축

---

## 범위

### 포함
- FastAPI 앱 기본 구조
- 레이어 분리 (Router → Service → LLM)
- 보안 미들웨어 (CORS, Rate Limit, Trusted Host)
- Pydantic 스키마 정의
- 기본 테스트 구조
- 환경변수 관리

### 제외
- RAG 파이프라인 (별도 Epic)
- 프로덕션 배포 설정
- 인증/인가

---

## Phase 구성

### Phase 1: 프로젝트 초기화
- [ ] 디렉토리 구조 생성
- [ ] 의존성 정의 (requirements.txt)
- [ ] 환경변수 설정 (.env.example)

### Phase 2: 코어 구현
- [ ] config.py (Pydantic Settings)
- [ ] schemas (request.py, response.py)
- [ ] main.py (FastAPI 앱)

### Phase 3: 서비스 레이어
- [ ] llm_service.py (Ollama 호출)
- [ ] prompt_builder.py
- [ ] project_resolver.py
- [ ] context_loader.py

### Phase 4: 보안 미들웨어
- [ ] security.py (CORS, Trusted Host)
- [ ] rate_limiter.py
- [ ] request_id.py
- [ ] error_handler.py
- [ ] guardrails.py

### Phase 5: 테스트
- [ ] conftest.py
- [ ] 단위 테스트
- [ ] 통합 테스트

---

## 완료 기준

- [ ] `uvicorn app.main:app --reload` 정상 실행
- [ ] `/api/v1/chat` 엔드포인트 동작
- [ ] Rate limiting 동작 확인
- [ ] 모든 테스트 통과
- [ ] 문서 업데이트

---

## 기술 결정 사항

| 항목 | 선택 | 이유 |
|------|------|------|
| Rate Limiter | slowapi | FastAPI 친화적, 간단 |
| 설정 관리 | pydantic-settings | 타입 안전, 검증 |
| 로깅 | structlog | 구조화된 JSON 로깅 |

---

## 참고

- [developmentGuide.md](../../../developmentGuide.md)
- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
