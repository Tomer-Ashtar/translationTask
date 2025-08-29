"""
Integration tests for the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app
from app.services.translation_service import TranslationService
from app.routes.translation import get_translation_service


class TestTranslationAPI:
    """Test cases for the translation API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
    
    @patch('app.routes.translation.get_translation_service')
    def test_translate_success(self, mock_get_service):
        """Test successful translation."""
        # Create a mock service
        mock_service = TranslationService()
        mock_service.translate = lambda text, source_lang, target_lang: "Translated text"
        mock_get_service.return_value = mock_service
        
        request_data = {
            "text": "Hello world",
            "source_lang": "en",
            "target_lang": "he"
        }
        
        response = self.client.post("/translate", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["translated_text"] == "Translated text"
        assert data["source_lang"] == "en"
        assert data["target_lang"] == "he"
        assert data["original_text"] == "Hello world"
    
    def test_translate_invalid_request(self):
        """Test translation with invalid request data."""
        request_data = {
            "text": "",  # Empty text
            "source_lang": "en",
            "target_lang": "he"
        }
        
        response = self.client.post("/translate", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_translate_same_languages(self):
        """Test translation with same source and target languages."""
        request_data = {
            "text": "Hello",
            "source_lang": "en",
            "target_lang": "en"
        }
        
        response = self.client.post("/translate", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_translate_unsupported_language(self):
        """Test translation with unsupported language."""
        request_data = {
            "text": "Hello",
            "source_lang": "en",
            "target_lang": "fr"  # French not supported
        }
        
        response = self.client.post("/translate", json=request_data)
        assert response.status_code == 422  # Validation error
    
    @patch('app.routes.translation.get_translation_service')
    def test_translate_word_limit_exceeded(self, mock_get_service):
        """Test translation with text exceeding 10 word limit."""
        # Create a mock service that raises ValueError
        mock_service = TranslationService()
        def raise_error(*args, **kwargs):
            raise ValueError("Text exceeds maximum length of 10 words. Current text has 15 words.")
        mock_service.translate = raise_error
        mock_get_service.return_value = mock_service
        
        request_data = {
            "text": "This is a very long text that definitely exceeds the maximum limit of ten words allowed",
            "source_lang": "en",
            "target_lang": "he"
        }
        
        response = self.client.post("/translate", json=request_data)
        assert response.status_code == 400  # Business validation error
        assert "exceeds maximum length" in response.json()["detail"]
    
    @patch('app.routes.translation.get_translation_service')
    def test_translate_service_error(self, mock_get_service):
        """Test translation when service raises an error."""
        # Create a mock service that raises TranslationError
        mock_service = TranslationService()
        def raise_error(*args, **kwargs):
            raise Exception("Translation failed")
        mock_service.translate = raise_error
        mock_get_service.return_value = mock_service
        
        request_data = {
            "text": "Hello",
            "source_lang": "en",
            "target_lang": "he"
        }
        
        response = self.client.post("/translate", json=request_data)
        assert response.status_code == 500
        data = response.json()
        assert data["error"] == "Translation Error"
        assert data["detail"] == "Translation failed"
    
    @patch('app.routes.translation.get_translation_service')
    def test_supported_languages_endpoint(self, mock_get_service):
        """Test supported languages endpoint."""
        # Create a mock service that returns language pairs
        mock_service = TranslationService()
        mock_service.get_supported_language_pairs = lambda: {
            "he-ru": "model1", "ru-he": "model2"
        }
        mock_get_service.return_value = mock_service
        
        response = self.client.get("/languages/supported")
        assert response.status_code == 200
        
        data = response.json()
        assert "supported_language_pairs" in data
        assert "language_codes" in data
        assert "he" in data["language_codes"]
        assert "ru" in data["language_codes"]
        assert "en" in data["language_codes"]