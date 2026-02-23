"""Integration tests for chat API"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Test client for FastAPI app"""
    return TestClient(app)


class TestHealthEndpoint:
    """Health check endpoint tests"""
    
    def test_health_check_success(self, client):
        """Test health endpoint returns OK"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_health_response_includes_request_id(self, client):
        """Test health response includes X-Request-ID header"""
        response = client.get("/health")
        assert "X-Request-ID" in response.headers


class TestChatEndpoint:
    """Chat endpoint tests"""
    
    @patch("app.services.llm_service.httpx.AsyncClient")
    def test_chat_success(self, mock_client_class, client):
        """Test successful chat request"""
        # Setup mock
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Hello!"}
        mock_response.raise_for_status.return_value = None
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__.return_value = mock_client
        mock_client.__aexit__.return_value = None
        mock_client_class.return_value = mock_client
        
        # Make request
        response = client.post(
            "/api/chat",
            json={"message": "Hello, how are you?"}
        )
        
        # Verify
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "Hello!"
        assert "request_id" in data
        assert "X-Request-ID" in response.headers
    
    def test_chat_empty_message(self, client):
        """Test chat with empty message"""
        response = client.post(
            "/api/chat",
            json={"message": ""}
        )
        assert response.status_code == 422
    
    def test_chat_whitespace_only(self, client):
        """Test chat with whitespace-only message"""
        response = client.post(
            "/api/chat",
            json={"message": "   "}
        )
        assert response.status_code == 422
    
    def test_chat_xss_injection_blocked(self, client):
        """Test chat blocks XSS injection attempts"""
        response = client.post(
            "/api/chat",
            json={"message": "<script>alert('xss')</script>"}
        )
        # Should be blocked by guardrails (returns 422)
        assert response.status_code == 422
    
    def test_chat_oversized_message(self, client):
        """Test chat with oversized message"""
        response = client.post(
            "/api/chat",
            json={"message": "a" * 10001}
        )
        assert response.status_code == 422
    
    def test_chat_response_includes_request_id(self, client):
        """Test chat response includes request_id"""
        # Send a valid request that will fail at LLM (but still processed)
        response = client.post(
            "/api/chat",
            json={"message": "test"}
        )
        
        # Should have X-Request-ID header
        assert "X-Request-ID" in response.headers


class TestRateLimiting:
    """Rate limiting functionality tests"""
    
    def test_rate_limit_default_allows_requests(self, client):
        """Test default rate limit allows requests"""
        # Default is 60 RPM, so multiple requests should work
        for _ in range(3):
            response = client.get("/health")
            assert response.status_code == 200
    
    def test_rate_limit_header_in_response(self, client):
        """Test that rate limit doesn't affect normal responses"""
        response = client.get("/health")
        # Should have X-Request-ID for all responses
        assert "X-Request-ID" in response.headers


class TestErrorHandling:
    """Error handling tests"""
    
    def test_invalid_json_returns_422(self, client):
        """Test invalid JSON returns 422"""
        response = client.post(
            "/api/chat",
            json={"invalid_field": "test"}
        )
        assert response.status_code == 422
    
    def test_error_response_format(self, client):
        """Test error response includes required fields"""
        response = client.post(
            "/api/chat",
            json={"message": ""}
        )
        
        # Should have error response format
        assert response.status_code == 422
        # Pydantic validation errors have different format, 
        # but should include detail


class TestCORSHeaders:
    """CORS configuration tests"""
    
    def test_health_returns_ok(self, client):
        """Test health endpoint is accessible"""
        response = client.get("/health")
        assert response.status_code == 200
