# Active Context

## Current Focus
Multi-Environment Deployment Epic (Phase 1-3) - Complete

## Recent Changes
- ✅ Phase 1: Environment-aware configuration (APP_ENV, .env.{env}, pip-tools lock)
- ✅ Phase 2: Dockerfile & Docker Compose (multi-stage build, local/staging/prod)
- ✅ Phase 3: GitHub Actions CI/CD pipeline (Tailscale, auto-deploy, Trivy scan)
- All 51 tests passing with new configuration
- Git commits successfully created for each phase

## Implementation Summary

### Phase 1: Environment-aware Configuration
- **Config System**: `app/core/config.py` reads `.env.{APP_ENV}` dynamically
- **Dependencies**: `requirements.in` → `pip-compile` → `requirements.txt` (lock file)
- **Environment Files**: `.env.local`, `.env.staging`, `.env.production` (git-ignored)
- **ALLOWED_ORIGINS Parsing**: JSON array format `["https://a.com"]` for pydantic-settings v2
- **Default**: `APP_ENV=local` when not set

### Phase 2: Docker & Docker Compose
- **Dockerfile**: Multi-stage build (base → test → production)
- **docker-compose.yml**: Local with hot reload (volume mount, `--reload`)
- **docker-compose.staging.yml**: Port 8001, image-based (no build)
- **docker-compose.prod.yml**: Port 8000, immutable `sha-{hash}` tags
- **.dockerignore**: Excludes venv, __pycache__, .env*, docs, etc.

### Phase 3: GitHub Actions CI/CD
- **deploy-staging.yml**: 
  - Triggered on `staging` branch push
  - Jobs: test (pytest, APP_ENV=local) → scan (Trivy, CRITICAL fails) → build & push → deploy (auto)
  - Auto-deploys to staging environment without approval
  - Health check with 5 retries (exponential backoff: 3s, 6s, 9s, 12s, 15s)

- **deploy-prod.yml**:
  - Triggered on `main` branch push
  - Same test/scan/build as staging
  - Deploy job requires manual approval (GitHub Environment)
  - Updates docker-compose.prod.yml with SHA tag before deployment
  - Health check on port 8000

## Architecture
```
Code Push
  ├─ staging branch → GitHub Actions (test/scan/build) → Push to ghcr.io:staging → SSH to Mac Mini → Deploy auto
  └─ main branch → GitHub Actions (test/scan/build) → Push to ghcr.io:latest + sha-{hash} → Manual approval → Deploy

Docker Compose
  ├─ Local: Build from Dockerfile, volume mount app/, hot reload
  ├─ Staging: ghcr.io/user/repo:staging, port 8001, env from .env.staging
  └─ Prod: ghcr.io/user/repo:sha-{hash}, port 8000, env from .env.production
```

## Tech Stack
- FastAPI 0.131 + Pydantic 2.12
- Python 3.12 slim base image
- pip-tools for dependency locking
- GitHub Actions with Tailscale + appleboy/ssh-action
- Trivy for container scanning
- Docker multi-stage builds

## Acceptance Criteria Status
- [x] All Phase 1 criteria met (config, pip-tools, multi-env)
- [x] All Phase 2 criteria met (Dockerfile, Compose, hot reload)
- [x] All Phase 3 criteria met (GitHub Actions, Trivy, Tailscale)
- [x] Existing tests (51) passing with new config
- [x] Environment-specific secrets & variables ready for GitHub setup

## GitHub Setup Required (Manual)
1. Create environments: `staging`, `production` (production requires reviewer approval)
2. Repository Secrets: `SSH_PRIVATE_KEY`, `TS_OAUTH_CLIENT_ID`, `TS_OAUTH_SECRET`, `GITHUB_TOKEN`
3. Staging Variables: `MACMINI_TAILSCALE_IP`, `MACMINI_USER`, `MODEL_NAME`, `ALLOWED_ORIGINS`, `RATE_LIMIT_RPM`, `LOG_LEVEL`
4. Production Variables: Same as staging (with prod-specific values)
5. Mac Mini prerequisites: `docker login ghcr.io`, `~/.ssh/authorized_keys` contains GitHub runner key

## Next Steps
- Manual: Set up GitHub Environments & Secrets/Variables
- Manual: Configure Tailscale ACL with `tag:ci` for Mac Mini access
- Manual: Test full CI/CD pipeline with staging branch push
- Future: Health check endpoints refinement (Ollama readiness probe)
- Future: Container resource limits after production testing

## Known Limitations
- Ollama remains bare metal (GPU/Metal access needed)
- No persistent storage configured yet
- Docker login to ghcr.io must be done manually on Mac Mini first
- No automated alerts/monitoring (future epic)

---
Last Updated: 2026-02-23 (Phase 1-3 Complete)
