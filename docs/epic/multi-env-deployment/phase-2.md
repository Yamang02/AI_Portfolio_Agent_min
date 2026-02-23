# Phase 2: Dockerfile & Docker Compose

## Scope

- `Dockerfile` 작성 (멀티스테이지: test / production)
- `docker-compose.local.yml` - hot reload, volume mount
- `docker-compose.staging.yml` - staging 컨테이너 (port 8001)
- `docker-compose.prod.yml` - prod 컨테이너 (port 8000)
- `.dockerignore` 작성

## Commit

chore: add Dockerfile and Docker Compose for all environments

## Environment

Mac Mini M4 (macOS) + OrbStack으로 컨테이너를 관리한다.
OrbStack은 macOS에서 `host.docker.internal`을 자동으로 제공하므로
`extra_hosts: host.docker.internal:host-gateway` 설정이 불필요하다.
(해당 설정은 Linux Docker에서만 필요한 workaround다.)

## Implementation

### Dockerfile

```dockerfile
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# test stage: CI에서 이미지 빌드 전 테스트 실행용
FROM base AS test
COPY . .
RUN pytest tests/

# production stage: 실제 배포 이미지
FROM base AS production
COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.local.yml

```yaml
services:
  fastapi:
    build:
      context: .
      target: production
    ports:
      - "8000:8000"
    env_file: .env.local
    volumes:
      - ./app:/app/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    restart: unless-stopped
```

### docker-compose.staging.yml

```yaml
services:
  fastapi:
    image: ghcr.io/{owner}/local-llm-server:staging
    ports:
      - "8001:8000"
    env_file: .env.staging
    restart: unless-stopped
```

### docker-compose.prod.yml

이미지 태그는 `:latest`를 사용하지 않는다.
CI가 배포 시점에 `sha-{github.sha}` 태그로 이 파일을 갱신해서 서버로 전달한다.

```yaml
services:
  fastapi:
    image: ghcr.io/{owner}/local-llm-server:sha-{hash}  # CI가 치환
    ports:
      - "8000:8000"
    env_file: .env.production
    restart: unless-stopped
```

### .dockerignore

```
.env*
venv/
__pycache__/
.pytest_cache/
*.pyc
.git/
memory-bank/
docs/
```

## Notes

### host.docker.internal

OrbStack(macOS)에서는 컨테이너가 호스트(Mac Mini)의 Ollama(`localhost:11434`)에
`host.docker.internal:11434`로 접근할 수 있다. 별도 설정 불필요.

Linux Docker라면 `extra_hosts: - "host.docker.internal:host-gateway"` 추가가 필요하지만
현재 환경(Mac Mini + OrbStack)에서는 해당 없다.

### 헬스 엔드포인트

현재 `/health`는 앱 프로세스 생존만 확인한다.
Ollama 연결까지 확인하는 `/health/ready`는 다음 epic(Ollama 가용성 처리)에서 다룬다.
CI 배포 헬스체크는 `/health`를 사용한다.

### 리소스 제한

컨테이너 CPU/메모리 제한은 현 단계에서 적용하지 않는다.
Mac Mini 리소스의 대부분을 Ollama가 사용하며, FastAPI 컨테이너는 경량이다.
실측 데이터가 생기면 별도로 추가한다.

### 로컬 실행

```bash
docker compose -f docker-compose.local.yml up
```

## Acceptance Criteria

- [ ] `docker compose -f docker-compose.local.yml up` 으로 로컬 서버 실행
- [ ] 로컬: 코드 변경 시 자동 reload 동작
- [ ] staging/prod: `image` 기반으로 실행 (build 없음)
- [ ] prod Compose 파일의 이미지 태그가 `sha-{hash}` 형식
- [ ] 컨테이너 내부에서 `host.docker.internal:11434`로 Ollama 호출 성공
- [ ] Mac Mini 재부팅 후 staging/prod 컨테이너 자동 재시작 (`restart: unless-stopped`)
- [ ] `/health` 엔드포인트 응답 확인
