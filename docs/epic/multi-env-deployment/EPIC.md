# Epic: Multi-Environment Deployment

## Overview

Mac Mini에서 동작하는 FastAPI LLM 서버를 local / staging / production 3개 환경으로 분리한다.
Ollama는 단일 프로세스를 공유하되, FastAPI 서버는 환경별로 별도 프로세스와 포트를 사용한다.
Cloudflare Tunnel은 이미 구성 완료 상태이며, staging과 prod는 동일한 서비스 토큰을 사용한다.

## Goals

- `APP_ENV` 환경변수 기반으로 설정 파일을 동적 로드 (`env.{APP_ENV}`)
- Mac Mini에서 staging/prod FastAPI 서버를 각각 독립 프로세스로 운영
- macOS launchd를 통한 서비스 자동 실행 및 관리

## Architecture

```
[Local]
  Windows Docker 백엔드
      | SSH 터널 (port 8000)
  Mac Mini
      └── FastAPI local (port 8000) → Ollama (11434)

[Staging / Production]
  GCP 백엔드
      | Cloudflare Tunnel (동일 서비스 토큰)
  Mac Mini
      ├── FastAPI staging (port 8001) → Ollama (11434)
      └── FastAPI prod    (port 8000) → Ollama (11434)
```

## Out of Scope

- Cloudflare Tunnel 설정 (완료)
- 서비스 토큰 분리 (의도적으로 미적용)
- FastAPI 레벨 인증 미들웨어 (Cloudflare Access에서 처리)
- Docker Compose 기반 배포

## Phases

| Phase | Title | Commit Type |
|-------|-------|-------------|
| 1 | Environment-aware Configuration | chore |
| 2 | macOS launchd Service Setup | chore |

## Acceptance Criteria

- [ ] `APP_ENV=local` 실행 시 `.env.local` 로드
- [ ] `APP_ENV=staging` 실행 시 `.env.staging` 로드
- [ ] `APP_ENV=production` 실행 시 `.env.production` 로드
- [ ] staging 서버 port 8001, prod 서버 port 8000으로 독립 실행
- [ ] Mac Mini 재부팅 시 staging/prod 서버 자동 시작
- [ ] 기존 테스트 전체 통과
