# Phase 1: Environment-aware Configuration

## Scope

- `APP_ENV` 환경변수에 따라 `.env.{APP_ENV}` 파일을 동적으로 로드하도록 `app/core/config.py` 수정
- `.env.local`, `.env.staging`, `.env.production` 파일 생성
- `.env.example` 업데이트

## Commit

chore: add multi-environment config support via APP_ENV

## Implementation

`app/core/config.py`:

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

`.env.local`:
```
APP_ENV=local
OLLAMA_URL=http://localhost:11434
MODEL_NAME=llama3:8b
ALLOWED_ORIGINS=*
RATE_LIMIT_RPM=60
LOG_LEVEL=DEBUG
```

`.env.staging`:
```
APP_ENV=staging
OLLAMA_URL=http://localhost:11434
MODEL_NAME=llama3:8b
ALLOWED_ORIGINS=https://staging.example.com
RATE_LIMIT_RPM=30
LOG_LEVEL=INFO
```

`.env.production`:
```
APP_ENV=production
OLLAMA_URL=http://localhost:11434
MODEL_NAME=llama3:8b
ALLOWED_ORIGINS=https://example.com
RATE_LIMIT_RPM=60
LOG_LEVEL=INFO
```

## Acceptance Criteria

- [ ] `APP_ENV=local` 실행 시 `.env.local` 로드
- [ ] `APP_ENV=staging` 실행 시 `.env.staging` 로드
- [ ] `APP_ENV=production` 실행 시 `.env.production` 로드
- [ ] `APP_ENV` 미설정 시 `.env.local` 기본값으로 fallback
- [ ] `.env.local`, `.env.staging`, `.env.production` 모두 `.gitignore`에 추가
- [ ] `.env.example`에 `APP_ENV` 항목 추가
- [ ] 기존 테스트 전체 통과 (설정 로드 방식 변경으로 인한 회귀 없음)
