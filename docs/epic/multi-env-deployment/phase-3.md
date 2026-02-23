# Phase 3: GitHub Actions CI/CD Pipeline

## Scope

- `.github/workflows/deploy-staging.yml` - staging 자동 배포
- `.github/workflows/deploy-prod.yml` - prod 배포 (수동 승인)
- GitHub Environments, Secrets, Variables 설정 가이드

## Commit

chore: add GitHub Actions CI/CD pipeline with Tailscale deployment

## GitHub 설정

### Environments

```
GitHub Repository → Settings → Environments

staging
  └── (protection rules 없음)

production
  └── Required reviewers: {본인 계정}
```

### Secrets (Repository 공통)

| Key | 설명 | 권한 |
|-----|------|------|
| `SSH_PRIVATE_KEY` | Mac Mini SSH 접속용 개인키 | - |
| `TS_OAUTH_CLIENT_ID` | Tailscale OAuth Client ID | - |
| `TS_OAUTH_SECRET` | Tailscale OAuth Secret | - |
| `GHCR_TOKEN` | GitHub Container Registry PAT | `write:packages` 만 부여. `repo` 권한 불필요 |

GHCR_TOKEN 발급: GitHub → Settings → Developer settings → Personal access tokens → `write:packages` 선택.

### Variables (Environment별)

| Key | staging | production |
|-----|---------|------------|
| `MACMINI_TAILSCALE_IP` | 100.x.x.x | 100.x.x.x |
| `MACMINI_USER` | server | server |
| `MODEL_NAME` | llama3:8b | llama3:8b |
| `ALLOWED_ORIGINS` | https://staging.example.com | https://example.com |
| `RATE_LIMIT_RPM` | 30 | 60 |
| `LOG_LEVEL` | INFO | INFO |
| `COMPOSE_FILE` | docker-compose.staging.yml | docker-compose.prod.yml |

## Implementation

### .github/workflows/deploy-staging.yml

```yaml
name: Deploy to Staging

on:
  push:
    branches: [staging]

jobs:
  test:
    runs-on: ubuntu-latest
    env:
      APP_ENV: local        # .env.local 없이 기본값으로 실행, Ollama는 mock
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest tests/

  scan:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build image for scanning
        run: docker build --target production -t scan-target .
      - name: Trivy vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: scan-target
          severity: CRITICAL       # CRITICAL만 fail, HIGH는 warning
          exit-code: "1"
          ignore-unfixed: true

  build-and-push:
    needs: scan
    runs-on: ubuntu-latest
    outputs:
      image_tag: ${{ steps.meta.outputs.sha_tag }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GHCR_TOKEN }}
      - name: Set image tags
        id: meta
        run: |
          SHA_TAG="sha-${{ github.sha }}"
          echo "sha_tag=${SHA_TAG}" >> $GITHUB_OUTPUT
      - uses: docker/build-push-action@v5
        with:
          context: .
          target: production
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:staging
            ghcr.io/${{ github.repository }}:${{ steps.meta.outputs.sha_tag }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - uses: tailscale/github-action@v2
        with:
          oauth-client-id: ${{ secrets.TS_OAUTH_CLIENT_ID }}
          oauth-secret: ${{ secrets.TS_OAUTH_SECRET }}
          tags: tag:ci

      - name: Write env file
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ vars.MACMINI_TAILSCALE_IP }}
          username: ${{ vars.MACMINI_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cat > ~/local-llm-server/.env.staging << EOF
            APP_ENV=staging
            OLLAMA_URL=http://host.docker.internal:11434
            MODEL_NAME=${{ vars.MODEL_NAME }}
            ALLOWED_ORIGINS=${{ vars.ALLOWED_ORIGINS }}
            RATE_LIMIT_RPM=${{ vars.RATE_LIMIT_RPM }}
            LOG_LEVEL=${{ vars.LOG_LEVEL }}
            EOF

      - name: Deploy
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ vars.MACMINI_TAILSCALE_IP }}
          username: ${{ vars.MACMINI_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd ~/local-llm-server
            docker compose -f ${{ vars.COMPOSE_FILE }} pull
            docker compose -f ${{ vars.COMPOSE_FILE }} up -d
            docker image prune -f

      - name: Health check
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ vars.MACMINI_TAILSCALE_IP }}
          username: ${{ vars.MACMINI_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            for i in $(seq 1 5); do
              echo "Health check attempt $i..."
              if curl -sf http://localhost:8001/health; then
                echo "Health check passed"
                exit 0
              fi
              sleep $((i * 3))   # 3s, 6s, 9s, 12s, 15s (지수 백오프)
            done
            echo "Health check failed after 5 attempts"
            exit 1
```

### .github/workflows/deploy-prod.yml

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    env:
      APP_ENV: local
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: pytest tests/

  scan:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build image for scanning
        run: docker build --target production -t scan-target .
      - name: Trivy vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: scan-target
          severity: CRITICAL
          exit-code: "1"
          ignore-unfixed: true

  build-and-push:
    needs: scan
    runs-on: ubuntu-latest
    outputs:
      sha_tag: ${{ steps.meta.outputs.sha_tag }}
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GHCR_TOKEN }}
      - name: Set image tags
        id: meta
        run: |
          SHA_TAG="sha-${{ github.sha }}"
          echo "sha_tag=${SHA_TAG}" >> $GITHUB_OUTPUT
      - uses: docker/build-push-action@v5
        with:
          context: .
          target: production
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ steps.meta.outputs.sha_tag }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: production         # 수동 승인 게이트
    steps:
      - uses: actions/checkout@v4
      - uses: tailscale/github-action@v2
        with:
          oauth-client-id: ${{ secrets.TS_OAUTH_CLIENT_ID }}
          oauth-secret: ${{ secrets.TS_OAUTH_SECRET }}
          tags: tag:ci

      - name: Write env file
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ vars.MACMINI_TAILSCALE_IP }}
          username: ${{ vars.MACMINI_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cat > ~/local-llm-server/.env.production << EOF
            APP_ENV=production
            OLLAMA_URL=http://host.docker.internal:11434
            MODEL_NAME=${{ vars.MODEL_NAME }}
            ALLOWED_ORIGINS=${{ vars.ALLOWED_ORIGINS }}
            RATE_LIMIT_RPM=${{ vars.RATE_LIMIT_RPM }}
            LOG_LEVEL=${{ vars.LOG_LEVEL }}
            EOF

      - name: Update compose image tag
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ vars.MACMINI_TAILSCALE_IP }}
          username: ${{ vars.MACMINI_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            # prod compose 파일의 이미지 태그를 SHA로 교체
            sed -i "s|image: ghcr.io/.*/local-llm-server:.*|image: ghcr.io/${{ github.repository }}:${{ needs.build-and-push.outputs.sha_tag }}|" \
              ~/local-llm-server/docker-compose.prod.yml

      - name: Deploy
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ vars.MACMINI_TAILSCALE_IP }}
          username: ${{ vars.MACMINI_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd ~/local-llm-server
            docker compose -f docker-compose.prod.yml pull
            docker compose -f docker-compose.prod.yml up -d
            docker image prune -f

      - name: Health check
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ vars.MACMINI_TAILSCALE_IP }}
          username: ${{ vars.MACMINI_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            for i in $(seq 1 5); do
              echo "Health check attempt $i..."
              if curl -sf http://localhost:8000/health; then
                echo "Health check passed"
                exit 0
              fi
              sleep $((i * 3))
            done
            echo "Health check failed after 5 attempts"
            exit 1
```

## Mac Mini 사전 설정

최초 1회 필요:
```bash
# ghcr.io 로그인 (GHCR_TOKEN 사용)
echo $GHCR_TOKEN | docker login ghcr.io -u {github-username} --password-stdin
```

## Rollback

```bash
# 이전 SHA로 롤백
ssh server@<tailscale-ip>
cd ~/local-llm-server

# compose 파일의 태그를 이전 sha로 교체 후 재실행
sed -i "s|:sha-.*|:sha-{previous-hash}|" docker-compose.prod.yml
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

배포된 SHA 히스토리는 ghcr.io 이미지 태그 목록 또는 GitHub Actions 실행 기록에서 확인한다.

## Notes

- Tailscale OAuth 설정: Tailscale Admin Console → Settings → OAuth Clients
  `tag:ci` 태그를 Tailscale ACL에 Mac Mini 접근 허용으로 등록 필요
- `deploy-staging.yml`과 `deploy-prod.yml`의 test/scan/build job은 중복이지만
  브랜치별 독립 트리거를 위해 분리 유지
- Trivy `ignore-unfixed: true`로 패치가 없는 취약점은 무시. 실제 대응 가능한 것만 차단

## Acceptance Criteria

- [ ] `staging` 브랜치 push → test → Trivy scan → 빌드 → staging 자동 배포
- [ ] `main` 브랜치 push → test → Trivy scan → 빌드 → 수동 승인 → prod 배포
- [ ] CRITICAL 취약점 발견 시 CI fail
- [ ] prod 이미지 태그가 `sha-{hash}`로 고정되어 배포
- [ ] 배포 후 헬스체크 5회 재시도, 지수 백오프 적용
- [ ] `.env.staging` / `.env.production`이 GitHub Variables에서 Mac Mini로 생성
- [ ] pytest job이 `APP_ENV=local`로 실행되어 Ollama 미의존
- [ ] 이전 SHA 태그로 수동 롤백 가능
- [ ] 오래된 이미지 자동 정리 (`docker image prune`)
