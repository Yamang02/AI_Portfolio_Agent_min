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
