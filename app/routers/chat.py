"""Chat router - thin layer with no business logic"""

from fastapi import APIRouter, Depends, Request
from app.schemas.request import ChatRequest
from app.schemas.response import ChatResponse
from app.services.llm_service import OllamaService, get_llm_service
from app.core.guardrails import validate_input, validate_output

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: Request,
    chat_request: ChatRequest,
    llm_service: OllamaService = Depends(get_llm_service)
) -> ChatResponse:
    """
    Chat endpoint with LLM
    
    - Validates input with guardrails
    - Calls LLM service
    - Validates and returns response
    """
    # Get request ID from middleware
    request_id = getattr(request.state, "request_id", "unknown")
    
    # Validate input
    validated_input = validate_input(chat_request.message)
    
    # Call LLM service
    llm_response = await llm_service.generate(validated_input)
    
    # Validate output
    validated_output = validate_output(llm_response)
    
    return ChatResponse(
        response=validated_output,
        request_id=request_id
    )
