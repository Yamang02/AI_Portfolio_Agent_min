import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.llm_service import (
    OllamaService, 
    LLMServiceError
)


@pytest.mark.asyncio
class TestOllamaService:
    
    @pytest.fixture
    def service(self):
        return OllamaService(
            base_url="http://localhost:11434",
            model_name="llama3",
            timeout=10.0
        )
    
    @pytest.mark.asyncio
    async def test_generate_success(self, service):
        """Test successful LLM generation"""
        with patch("app.services.llm_service.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.json.return_value = {"response": "test response"}
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            
            result = await service.generate("test prompt")
            assert result == "test response"
            mock_client.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_timeout_error(self, service):
        """Test timeout error handling"""
        with patch("app.services.llm_service.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            
            with pytest.raises(LLMServiceError, match="timeout"):
                await service.generate("test prompt")
    
    @pytest.mark.asyncio
    async def test_generate_connection_error(self, service):
        """Test connection error handling"""
        with patch("app.services.llm_service.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client.post = AsyncMock(side_effect=httpx.ConnectError("connection failed"))
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            
            with pytest.raises(LLMServiceError, match="connect"):
                await service.generate("test prompt")
    
    @pytest.mark.asyncio
    async def test_generate_http_error(self, service):
        """Test HTTP error handling"""
        with patch("app.services.llm_service.httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "500 error", 
                request=MagicMock(), 
                response=mock_response
            )
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client.__aenter__.return_value = mock_client
            mock_client.__aexit__.return_value = None
            mock_client_class.return_value = mock_client
            
            with pytest.raises(LLMServiceError):
                await service.generate("test prompt")
