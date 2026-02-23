# Phase 2: macOS launchd Service Setup

## Scope

- `deploy/launchd/` 디렉토리에 staging/prod용 launchd plist 파일 생성
- 각 서비스는 Mac Mini 재부팅 시 자동 시작
- staging: port 8001, production: port 8000

## Commit

chore: add launchd plists for staging and prod FastAPI services

## Implementation

파일 위치: `deploy/launchd/`

```
deploy/launchd/
├── com.llm-server.staging.plist
├── com.llm-server.prod.plist
└── README.md
```

`com.llm-server.staging.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.llm-server.staging</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/bin/uvicorn</string>
        <string>app.main:app</string>
        <string>--host</string>
        <string>0.0.0.0</string>
        <string>--port</string>
        <string>8001</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>APP_ENV</key>
        <string>staging</string>
    </dict>
    <key>WorkingDirectory</key>
    <string>/path/to/local-llm-server</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/var/log/llm-server-staging.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/llm-server-staging.err</string>
</dict>
</plist>
```

`com.llm-server.prod.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.llm-server.prod</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/bin/uvicorn</string>
        <string>app.main:app</string>
        <string>--host</string>
        <string>0.0.0.0</string>
        <string>--port</string>
        <string>8000</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>APP_ENV</key>
        <string>production</string>
    </dict>
    <key>WorkingDirectory</key>
    <string>/path/to/local-llm-server</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/var/log/llm-server-prod.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/llm-server-prod.err</string>
</dict>
</plist>
```

설치 명령 (README.md에도 기재):
```bash
# /path/to를 실제 경로로 치환 후
cp deploy/launchd/com.llm-server.staging.plist ~/Library/LaunchAgents/
cp deploy/launchd/com.llm-server.prod.plist ~/Library/LaunchAgents/

launchctl load ~/Library/LaunchAgents/com.llm-server.staging.plist
launchctl load ~/Library/LaunchAgents/com.llm-server.prod.plist

# 상태 확인
launchctl list | grep llm-server
```

## Acceptance Criteria

- [ ] `deploy/launchd/com.llm-server.staging.plist` 존재
- [ ] `deploy/launchd/com.llm-server.prod.plist` 존재
- [ ] `deploy/launchd/README.md`에 설치/제거/상태 확인 명령 기재
- [ ] staging 서비스가 port 8001에서 `APP_ENV=staging`으로 동작
- [ ] prod 서비스가 port 8000에서 `APP_ENV=production`으로 동작
- [ ] Mac Mini 재부팅 후 두 서비스 자동 시작 확인
