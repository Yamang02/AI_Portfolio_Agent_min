from typing import Protocol
import httpx
from app.core.config import get_settings


class LLMServiceError(Exception):
    """LLM service-related errors"""
    pass


class LLMService(Protocol):
    """Protocol for LLM service implementations"""
    
    async def generate(self, prompt: str) -> str:
        """Generate response from LLM"""
        ...


class OllamaService:
    """Ollama LLM service implementation"""
    
    def __init__(self, base_url: str, model_name: str, timeout: float = 30.0):
        self.base_url = base_url
        self.model_name = model_name
        self.timeout = timeout
    
    async def generate(self, prompt: str) -> str:
        """Generate response from Ollama"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                return response.json()["response"]
        except httpx.TimeoutException as e:
            raise LLMServiceError(f"LLM service timeout: {str(e)}")
        except (httpx.ConnectError, httpx.RequestError) as e:
            raise LLMServiceError(f"Failed to connect to LLM service: {str(e)}")
        except Exception as e:
            raise LLMServiceError(f"LLM service error: {str(e)}")


def get_llm_service() -> OllamaService:
    """Dependency injection factory for LLM service"""
    settings = get_settings()
    return OllamaService(
        base_url=settings.ollama_url,
        model_name=settings.model_name
    )
