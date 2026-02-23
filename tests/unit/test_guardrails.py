"""Tests for guardrails module"""

import pytest
from app.core.guardrails import validate_input, validate_output
from app.core.exceptions import ValidationError


class TestValidateInput:
    """Test input validation and XSS filtering"""
    
    def test_valid_input(self):
        """Test valid input passes validation"""
        result = validate_input("Hello, this is a valid message")
        assert result == "Hello, this is a valid message"
    
    def test_input_whitespace_stripped(self):
        """Test whitespace is stripped from input"""
        result = validate_input("  hello world  ")
        assert result == "hello world"
    
    def test_empty_input_rejected(self):
        """Test empty input is rejected"""
        with pytest.raises(ValidationError, match="empty"):
            validate_input("")
    
    def test_whitespace_only_rejected(self):
        """Test whitespace-only input is rejected"""
        with pytest.raises(ValidationError, match="empty"):
            validate_input("   \t\n  ")
    
    def test_non_string_rejected(self):
        """Test non-string input is rejected"""
        with pytest.raises(ValidationError, match="string"):
            validate_input(123)  # type: ignore
    
    def test_script_tag_rejected(self):
        """Test script tags are rejected"""
        with pytest.raises(ValidationError, match="dangerous"):
            validate_input("hello <script>alert('xss')</script>")
    
    def test_javascript_url_rejected(self):
        """Test javascript: URLs are rejected"""
        with pytest.raises(ValidationError, match="dangerous"):
            validate_input("click here: javascript:alert('xss')")
    
    def test_event_handler_rejected(self):
        """Test event handlers are rejected"""
        with pytest.raises(ValidationError, match="dangerous"):
            validate_input('<img src=x onerror="alert(\'xss\')">')
    
    def test_eval_function_rejected(self):
        """Test eval() calls are rejected"""
        with pytest.raises(ValidationError, match="dangerous"):
            validate_input("eval(malicious_code)")
    
    def test_iframe_rejected(self):
        """Test iframes are rejected"""
        with pytest.raises(ValidationError, match="dangerous"):
            validate_input('<iframe src="malicious.com"></iframe>')
    
    def test_max_length_exceeded(self):
        """Test input exceeding max length is rejected"""
        with pytest.raises(ValidationError, match="exceeds maximum"):
            validate_input("a" * 10001)
    
    def test_max_length_boundary(self):
        """Test input at exact max length is accepted"""
        result = validate_input("a" * 10000)
        assert len(result) == 10000
    
    def test_document_access_rejected(self):
        """Test document access is rejected"""
        with pytest.raises(ValidationError, match="dangerous"):
            validate_input("document.cookie")
    
    def test_window_access_rejected(self):
        """Test window access is rejected"""
        with pytest.raises(ValidationError, match="dangerous"):
            validate_input("window.location")


class TestValidateOutput:
    """Test output validation"""
    
    def test_valid_output(self):
        """Test valid output passes validation"""
        result = validate_output("This is a valid response")
        assert result == "This is a valid response"
    
    def test_output_whitespace_stripped(self):
        """Test output whitespace is stripped"""
        result = validate_output("  response  \n")
        assert result == "response"
    
    def test_empty_output_rejected(self):
        """Test empty output is rejected"""
        with pytest.raises(ValidationError, match="empty"):
            validate_output("")
    
    def test_whitespace_only_output_rejected(self):
        """Test whitespace-only output is rejected"""
        with pytest.raises(ValidationError, match="empty"):
            validate_output("   \t\n  ")
    
    def test_non_string_output_rejected(self):
        """Test non-string output is rejected"""
        with pytest.raises(ValidationError, match="string"):
            validate_output(None)  # type: ignore
