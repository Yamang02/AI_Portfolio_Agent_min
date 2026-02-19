from fastapi import FastAPI
from app.schemas import ChatRequest, ChatResponse
from app.llm import call_llm

app = FastAPI(title="Local LLM Server")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    result = call_llm(req.message)
    return ChatResponse(response=result)
