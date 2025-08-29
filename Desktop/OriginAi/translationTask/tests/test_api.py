"""
Integration tests for the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app


class TestTranslationAPI:
    """Test cases for the translation API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["version"] == "1.0.0"
    
    @patch('app.main.translation_service')
    def test_health_check_healthy(self, mock_service):
        """Test health check when service is healthy."""
        mock_service.get_supported_language_pairs.return_value = {
            "he-ru": "model1", "ru-he": "model2"
        }
        mock_service.is_model_loaded.return_value = True
        
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "supported_language_pairs" in data
        assert "loaded_models" in data
    
    def test_health_check_service_unavailable(self):
        """Test health check when service is not initialized."""
        # This test runs before lifespan events, so service should be None
        with patch('app.main.translation_service', None):
            response = self.client.get("/health")
            assert response.status_code == 503
    
    @patch('app.main.translation_service')
    def test_translate_success(self, mock_service):
        """Test successful translation."""
        mock_service.translate.return_value = "Translated text"
        
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
    
    def test_translate_word_limit_exceeded(self):
        """Test translation with text exceeding 10 word limit."""
        request_data = {
            "text": "This is a very long text that definitely exceeds the maximum limit of ten words allowed",
            "source_lang": "en",
            "target_lang": "he"
        }
        
        response = self.client.post("/translate", json=request_data)
        assert response.status_code == 422  # Validation error
    
    @patch('app.main.translation_service')
    def test_translate_service_error(self, mock_service):
        """Test translation when service raises an error."""
        mock_service.translate.side_effect = Exception("Translation failed")
        
        request_data = {
            "text": "Hello",
            "source_lang": "en",
            "target_lang": "he"
        }
        
        response = self.client.post("/translate", json=request_data)
        assert response.status_code == 500
    
    @patch('app.main.translation_service')
    def test_batch_translate_success(self, mock_service):
        """Test successful batch translation."""
        mock_service.translate.side_effect = ["Text 1 translated", "Text 2 translated"]
        
        request_data = {
            "texts": ["Text 1", "Text 2"],
            "source_lang": "en",
            "target_lang": "he"
        }
        
        response = self.client.post("/translate/batch", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_count"] == 2
        assert len(data["translations"]) == 2
        assert data["translations"][0]["translated_text"] == "Text 1 translated"
        assert data["translations"][1]["translated_text"] == "Text 2 translated"
    
    def test_batch_translate_empty_list(self):
        """Test batch translation with empty text list."""
        request_data = {
            "texts": [],
            "source_lang": "en",
            "target_lang": "he"
        }
        
        response = self.client.post("/translate/batch", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_batch_translate_too_many_texts(self):
        """Test batch translation with too many texts."""
        request_data = {
            "texts": ["text"] * 101,  # Exceeds max limit of 100
            "source_lang": "en",
            "target_lang": "he"
        }
        
        response = self.client.post("/translate/batch", json=request_data)
        assert response.status_code == 422  # Validation error
    
    @patch('app.main.translation_service')
    def test_supported_languages_endpoint(self, mock_service):
        """Test supported languages endpoint."""
        mock_service.get_supported_language_pairs.return_value = {
            "he-ru": "model1", "ru-he": "model2"
        }
        
        response = self.client.get("/supported-languages")
        assert response.status_code == 200
        
        data = response.json()
        assert "supported_language_pairs" in data
        assert "language_codes" in data
        assert "he" in data["language_codes"]
        assert "ru" in data["language_codes"]
        assert "en" in data["language_codes"]