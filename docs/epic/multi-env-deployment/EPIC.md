# Epic: Multi-Environment Deployment

## Overview

Mac Mini에서 동작하는 FastAPI LLM 서버를 local / staging / production 3개 환경으로 분리한다.
FastAPI 서버는 모든 환경에서 Docker로 실행해 일관성을 확보하고,
GitHub Actions + Tailscale을 통한 자동 배포 파이프라인을 구축한다.
Ollama는 GPU/Metal 직접 접근이 필요하므로 bare metal로 유지한다.

## Architecture

```
[Local]
  Windows Docker 백엔드
      | SSH 터널
  Mac Mini
      ├── Ollama (bare metal, port 11434)
      └── Docker: fastapi-local (port 8000, hot reload)

[Staging / Production]
  GCP 백엔드
      | Cloudflare Tunnel
  Mac Mini
      ├── Ollama (bare metal, port 11434)
      ├── Docker: fastapi-staging (port 8001)
      └── Docker: fastapi-prod    (port 8000)
```

## CI/CD Flow

```
Push to staging branch
    ↓ GitHub Actions (클라우드 러너)
    ├── pytest 실행
    ├── Docker 이미지 빌드
    └── ghcr.io에 push (:staging 태그)
    ↓ Tailscale로 Mac Mini SSH 접속
    ├── .env.staging 생성 (GitHub Secrets/Variables에서)
    └── docker compose pull → up -d

Push to main branch
    ↓ 동일 흐름, :latest 태그, prod 배포 (수동 승인)
```

## Image Registry

```
ghcr.io/{owner}/local-llm-server:latest    → prod
ghcr.io/{owner}/local-llm-server:staging   → staging
ghcr.io/{owner}/local-llm-server:sha-{hash} → 롤백용
```

## Environment Variable Management

| 항목 | 저장 위치 | 예시 |
|------|----------|------|
| 민감한 값 | GitHub Secrets | `SSH_PRIVATE_KEY` |
| 비민감한 설정 | GitHub Variables (환경별) | `MODEL_NAME`, `RATE_LIMIT_RPM` |
| .env.* 파일 | 배포 시 Mac Mini에서 생성 | git에 포함 안 됨 |

## Out of Scope

- Cloudflare Tunnel 설정 (완료)
- Tailscale 설정 (완료)
- Cloudflare 서비스 토큰 분리 (의도적으로 미적용)
- FastAPI 레벨 인증 미들웨어 (Cloudflare Access에서 처리)
- Ollama Docker화

## Phases

| Phase | Title | Commit Type |
|-------|-------|-------------|
| 1 | Environment-aware Configuration | chore |
| 2 | Dockerfile & Docker Compose | chore |
| 3 | GitHub Actions CI/CD Pipeline | chore |

## Key Decisions

| 항목 | 결정 |
|------|------|
| ALLOWED_ORIGINS 파싱 | CSV 형식, pydantic-settings 자동 처리 |
| 의존성 관리 | pip-tools (`requirements.in` → `requirements.txt` lock) |
| prod 이미지 태그 | `sha-{hash}` 고정 (`:latest`는 보조 용도) |
| 헬스 엔드포인트 | `/health` (liveness), `/health/ready` (Ollama 포함)는 다음 epic |
| 이미지 보안 스캔 | Trivy, CRITICAL만 fail (`ignore-unfixed: true`) |
| SBOM | 현 단계 제외 |
| 모니터링/알림 | 현 단계 제외, 별도 epic |
| 컨테이너 리소스 제한 | 현 단계 제외, 실측 후 추가 |

## Acceptance Criteria

- [ ] 3개 환경 모두 Docker로 FastAPI 실행
- [ ] 로컬: hot reload 동작, `docker compose up` 한 줄로 시작
- [ ] staging/prod: 독립 컨테이너, 포트 분리 (8001 / 8000)
- [ ] `ALLOWED_ORIGINS` CSV 형식이 `list[str]`으로 올바르게 파싱됨
- [ ] `requirements.in` + `requirements.txt` lock file 구조 적용
- [ ] Mac Mini 재시작 시 staging/prod 컨테이너 자동 복구 (`restart: unless-stopped`)
- [ ] staging 브랜치 push → test → Trivy scan → staging 자동 배포
- [ ] main 브랜치 push → test → Trivy scan → 수동 승인 → prod 배포
- [ ] CRITICAL 취약점 발견 시 CI fail
- [ ] prod 이미지 태그가 `sha-{hash}`로 고정
- [ ] 배포 후 헬스체크 5회 재시도 (지수 백오프)
- [ ] GitHub Secrets/Variables에서 환경변수 주입, .env.* 파일은 git 미포함
- [ ] pytest가 `APP_ENV=local`로 실행되어 Ollama 미의존
- [ ] 기존 테스트 전체 통과
