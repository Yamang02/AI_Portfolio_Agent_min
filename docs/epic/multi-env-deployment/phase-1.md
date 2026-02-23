# Phase 1: Environment-aware Configuration

## Scope

- `APP_ENV` 환경변수에 따라 `.env.{APP_ENV}` 파일을 동적으로 로드하도록 `app/core/config.py` 수정
- `ALLOWED_ORIGINS` CSV 파싱 처리
- pip-tools 도입 (`requirements.in` → `requirements.txt` lock file)
- `.env.local`, `.env.staging`, `.env.production` 템플릿 생성
- `.env.example` 업데이트
- `.gitignore`에 `.env.*` 추가 (`.env.example` 제외)

## Commit

chore: add multi-environment config and pip-tools dependency locking

## Implementation

### app/core/config.py

```python
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

_env = os.getenv("APP_ENV", "local")

class Settings(BaseSettings):
    app_env: str = "local"
    ollama_url: str = "http://localhost:11434"
    model_name: str = "llama3:8b"
    allowed_origins: list[str] = ["*"]
    rate_limit_rpm: int = 60
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=f".env.{_env}",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

`allowed_origins: list[str]`에 pydantic-settings v2는 CSV 형식을 자동으로 파싱한다.
환경변수에 `ALLOWED_ORIGINS=https://a.com,https://b.com` 형식으로 작성하면 된다.
JSON 배열(`["..."]`) 형식도 지원하지만 GitHub Variables에서 따옴표 이스케이프가 번거로우므로 CSV를 표준으로 사용한다.

### 의존성 관리: pip-tools

직접 의존성은 `requirements.in`에 버전 범위로 명시하고,
`pip-compile`이 생성한 `requirements.txt`를 lock file로 사용한다.

```
requirements.in   ← 직접 의존성 (git 포함)
requirements.txt  ← pip-compile 생성 lock file (git 포함)
```

`requirements.in` 예시:
```
fastapi>=0.109
pydantic>=2.0
pydantic-settings>=2.0
httpx>=0.27
uvicorn[standard]>=0.29
```

lock file 갱신 명령:
```bash
pip install pip-tools
pip-compile requirements.in
```

Dockerfile에서는 `requirements.txt`(lock file)만 사용:
```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```

### .env 파일

`.env.example` (git 포함):
```
APP_ENV=local
OLLAMA_URL=http://localhost:11434
MODEL_NAME=llama3:8b
ALLOWED_ORIGINS=*
RATE_LIMIT_RPM=60
LOG_LEVEL=DEBUG
```

`.env.local` (git 제외, 로컬 실행용):
```
APP_ENV=local
OLLAMA_URL=http://host.docker.internal:11434
MODEL_NAME=llama3:8b
ALLOWED_ORIGINS=*
RATE_LIMIT_RPM=60
LOG_LEVEL=DEBUG
```

`.env.staging` / `.env.production` (git 제외, CI가 배포 시 생성):
```
APP_ENV=staging
OLLAMA_URL=http://host.docker.internal:11434
MODEL_NAME=llama3:8b
ALLOWED_ORIGINS=https://staging.example.com
RATE_LIMIT_RPM=30
LOG_LEVEL=INFO
```

## Notes

- `lru_cache`로 인해 테스트 간 설정 누수가 발생할 수 있다.
  테스트에서 설정을 오버라이드해야 할 경우 `get_settings.cache_clear()` 호출 필요.
- 로컬 pytest 실행 시에는 `APP_ENV=local`이 기본값이므로 `.env.local`을 읽는다.
  Ollama 의존이 없는 unit test는 `OLLAMA_URL`을 mock으로 대체한다.

## Acceptance Criteria

- [ ] `APP_ENV=local` 실행 시 `.env.local` 로드
- [ ] `APP_ENV=staging` 실행 시 `.env.staging` 로드
- [ ] `APP_ENV=production` 실행 시 `.env.production` 로드
- [ ] `APP_ENV` 미설정 시 `.env.local` 기본값으로 fallback
- [ ] `ALLOWED_ORIGINS=https://a.com,https://b.com` CSV 형식이 `list[str]`으로 올바르게 파싱됨
- [ ] `requirements.in` + `requirements.txt` (lock) 구조 적용
- [ ] `.gitignore`에 `.env.local`, `.env.staging`, `.env.production` 추가
- [ ] `.env.example`에 `APP_ENV` 항목 및 CSV 형식 주석 추가
- [ ] 기존 테스트 전체 통과
