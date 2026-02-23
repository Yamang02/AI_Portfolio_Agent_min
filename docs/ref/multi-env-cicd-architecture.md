# 로컬 LLM 서버 멀티 환경 구성 및 CI/CD 설계

Mac Mini에 FastAPI + Ollama를 올려두고 이걸 local/staging/prod 3개 환경으로 운영하면서 GitHub Actions 자동 배포까지 붙이는 과정에서 결정한 것들을 정리한다.

---

## 출발점

포트폴리오 사이트용 AI 에이전트 서버다. Mac Mini가 Ollama를 돌리고 FastAPI가 그 앞에서 API를 제공한다. 윈도우 쪽 도커 개발 서버에서 맥미니를 SSH로 호출해서 쓰는 구조로 시작했고, 여기에 GCP 프로덕션 환경을 붙이려다 보니 환경 분리 설계가 필요해졌다.

---

## 환경 분리 전략

### 3개 환경의 역할

**Local**
- 윈도우 Docker 백엔드 → SSH 터널 → Mac Mini FastAPI
- SSH 터널 자체가 보안 레이어라 별도 인증 없음
- 개발 중 빠른 iteration이 목적

**Staging**
- GCP 백엔드 → Cloudflare Tunnel → Mac Mini FastAPI (port 8001)
- 새 코드 배포 전 검증용

**Production**
- GCP 백엔드 → Cloudflare Tunnel → Mac Mini FastAPI (port 8000)
- 안정 버전만 배포

Mac Mini 한 대가 staging과 prod 두 역할을 동시에 수행한다. Ollama는 공유 프로세스 하나인데, FastAPI 레이어만 포트로 분리하는 구조다.

### 환경 구분 방법

`APP_ENV` 환경변수 하나로 설정 파일을 동적으로 로드한다.

```python
_env = os.getenv("APP_ENV", "local")

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=f".env.{_env}")
```

`.env.local`, `.env.staging`, `.env.production` 파일은 git에 올리지 않고, 로컬은 직접 만들고 staging/prod는 배포 시점에 CI가 생성한다.

---

## Cloudflare 서비스 토큰: 환경별 분리 여부

Cloudflare Access의 서비스 토큰을 staging과 prod에서 같은 걸 쓸지 나눠 쓸지 고민했다.

**나눠야 하는 이유**
- staging에서 토큰이 유출되면 prod까지 뚫림
- Cloudflare 감사 로그에서 두 환경 트래픽이 섞임
- 토큰 교체 시 두 환경을 동시에 업데이트해야 함

**같이 써도 되는 경우**
- staging이 실험용이라 보안을 별도로 신경 쓰지 않는 상황
- 관리 오버헤드를 줄이고 싶을 때

이번 케이스는 staging 보안을 별도로 고려하지 않는 상황이라 동일 토큰을 쓰기로 했다. Cloudflare Tunnel 자체가 인증을 처리하므로 FastAPI 레벨에서는 별도 인증 미들웨어를 추가하지 않는다.

---

## Docker 도입

처음엔 uvicorn 직접 실행 + launchd로 프로세스를 관리하려 했다. CI/CD를 붙이는 시점에 Docker를 같이 도입하기로 했다.

### Ollama는 컨테이너 밖

Ollama가 Mac Mini의 GPU/Metal에 직접 접근해야 해서 컨테이너로 감쌀 수 없다. FastAPI만 Docker로 돌리고, 컨테이너 내부에서 `host.docker.internal:11434`로 Ollama를 호출한다.

Linux에서는 이 hostname이 자동으로 제공되지 않아서 Compose 파일에 명시가 필요하다.
```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

### 환경별 Compose 파일 분리

```
docker-compose.local.yml    - 개발용, hot reload, volume mount
docker-compose.staging.yml  - staging, ghcr.io 이미지 사용
docker-compose.prod.yml     - prod, ghcr.io 이미지 사용
```

로컬도 Docker를 쓰는 게 일관성 있다. 로컬은 volume mount로 코드 변경을 즉시 반영하고 `--reload` 옵션을 켜둔다. staging/prod는 이미지를 pull해서 그대로 실행한다.

```yaml
# local: 개발 편의성
volumes:
  - ./app:/app/app
command: uvicorn app.main:app --host 0.0.0.0 --reload

# staging/prod: 이미지 기반
image: ghcr.io/{owner}/local-llm-server:staging
```

`restart: unless-stopped`로 Mac Mini 재부팅 후 컨테이너 자동 복구를 처리한다. launchd plist를 따로 관리할 필요가 없어진다.

---

## CI/CD: GitHub Actions + Tailscale

### GitHub Actions 클라우드 러너가 Mac Mini에 직접 접근하는 방법

GitHub Actions의 클라우드 러너는 공인 IP가 없는 Mac Mini에 직접 접근할 수 없다. 이를 해결하는 방법이 두 가지 있다.

**Self-hosted Runner**
Mac Mini에 GitHub Actions runner 에이전트를 설치한다. 이 에이전트가 GitHub API를 polling하다가 job이 오면 당겨서 로컬에서 실행한다. 인바운드 연결이 전혀 없어서 공인 IP나 포트 개방이 필요 없다. 단, runner 데몬이 항상 Mac Mini에서 실행되고 있어야 한다.

**Tailscale + 클라우드 러너 (채택)**
`tailscale/github-action`을 쓰면 클라우드 러너가 job 실행 중에 내 Tailscale 네트워크에 합류한다. 그 상태에서 Mac Mini의 Tailscale IP(100.x.x.x)로 SSH 접속해서 배포 명령을 실행한다. 클라우드 배포와 워크플로우가 동일하고, Mac Mini에 추가 데몬이 없어도 된다.

이미 Tailscale이 설정되어 있어서 이 방향을 선택했다.

### 전체 배포 흐름

```
1. staging 브랜치에 push
2. 클라우드 러너: pytest 실행
3. 클라우드 러너: Docker 이미지 빌드 → ghcr.io에 push (:staging 태그)
4. Tailscale로 Mac Mini SSH 접속
5. Mac Mini: .env.staging 생성 (GitHub Variables/Secrets에서)
6. Mac Mini: docker compose pull → up -d
```

prod는 동일한 흐름이지만 GitHub Environment의 수동 승인 게이트를 거친다.

### 환경변수 관리

`.env.*` 파일은 git에 없고, 배포 시점에 CI가 생성한다.

```yaml
- name: Write env file
  script: |
    cat > ~/local-llm-server/.env.staging << EOF
    APP_ENV=staging
    MODEL_NAME=${{ vars.MODEL_NAME }}
    ALLOWED_ORIGINS=${{ vars.ALLOWED_ORIGINS }}
    EOF
```

GitHub에서 민감한 값(SSH 키, Tailscale OAuth)은 Secrets에, 비민감한 설정(모델명, rate limit)은 Variables에 보관한다. Variables는 GitHub UI에서 평문으로 확인할 수 있어서 설정 관리가 편하다.

환경별로 GitHub Environments를 분리해서 staging/prod가 각자 다른 Variables 값을 갖는다.

### 이미지 태그 전략

```
:staging      - staging 최신
:latest       - prod 최신
:sha-{hash}   - 롤백용
```

롤백은 `sha-{hash}` 태그로 특정 커밋의 이미지를 직접 실행한다.

---

## 결론

Mac Mini 한 대로 staging/prod를 동시에 운영하는 구조라 물리 자원 분리는 없다. 하지만 포트, 환경변수, Docker 컨테이너, CI/CD 파이프라인 레벨에서 충분히 분리된다.

핵심 결정들을 요약하면:
- Ollama는 bare metal, FastAPI만 Docker
- Cloudflare가 외부 인증 처리, FastAPI는 인증 미들웨어 없음
- Self-hosted runner 대신 Tailscale + 클라우드 러너로 "진짜 CI/CD"처럼 운영
- 환경변수는 GitHub에서 관리, 배포 시점에 .env 파일 생성
