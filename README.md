
```
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json"  -d "{\"message\": \"안녕하세요\"}"
```

```
Invoke-WebRequest -Uri http://localhost:8000/chat -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"message": "안녕하세요"}'

```