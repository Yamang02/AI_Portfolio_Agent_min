import pytest
from unittest.mock import AsyncMock
from app.services.llm_service import OllamaService


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing"""
    service = AsyncMock(spec=OllamaService)
    service.generate = AsyncMock(return_value="Mocked LLM response")
    return service
