import pytest
from pydantic import ValidationError

from app.schemas.request import ChatRequest
from app.schemas.response import ChatResponse


class TestChatRequest:
    def test_valid_message(self):
        req = ChatRequest(message="hello")
        assert req.message == "hello"

    def test_empty_message_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="")

    def test_whitespace_only_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="   ")

    def test_whitespace_stripped(self):
        req = ChatRequest(message="  hello  ")
        assert req.message == "hello"

    def test_max_length_boundary(self):
        req = ChatRequest(message="a" * 1000)
        assert len(req.message) == 1000

    def test_over_max_length_rejected(self):
        with pytest.raises(ValidationError):
            ChatRequest(message="a" * 1001)


class TestChatResponse:
    def test_valid_response(self):
        resp = ChatResponse(response="hello", request_id="abc-123")
        assert resp.response == "hello"
        assert resp.request_id == "abc-123"

    def test_missing_request_id_rejected(self):
        with pytest.raises(ValidationError):
            ChatResponse(response="hello")
