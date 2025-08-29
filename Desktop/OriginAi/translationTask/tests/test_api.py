"""
Integration tests for the FastAPI application.
"""

import pytest
import random
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app, translation_service
from app.core.exceptions import TranslationError
from app.core.translation_config import LANGUAGE_CODES, SUPPORTED_MODELS


class TestTranslationAPI:
    """Test cases for the translation API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        self.available_languages = list(LANGUAGE_CODES.keys())
    
    @patch('app.main.translation_service')
    def test_translate_success(self, mock_service):
        """Test successful translation."""
        # Get a valid language pair from supported models
        source_lang, target_lang = random.choice(list(SUPPORTED_MODELS.keys())).split('-')
        mock_service.translate.return_value = "Translated text"
        
        response = self.client.post("translations/translate", json={
            "text": "Sample text for translation",
            "source_lang": source_lang,
            "target_lang": target_lang
        })
        assert response.status_code == 200
        data = response.json()
        assert data["translated_text"] == "Translated text"
    
    def test_translate_validation(self):
        """Test translation input validation."""
        random_lang = random.choice(self.available_languages)
        
        # Test empty text
        response = self.client.post("translations/translate", json={
            "text": "",
            "source_lang": random_lang,
            "target_lang": random.choice([lang for lang in self.available_languages if lang != random_lang])
        })
        assert response.status_code == 422
        
        # Test same languages
        response = self.client.post("translations/translate", json={
            "text": "Hello",
            "source_lang": random_lang,
            "target_lang": random_lang
        })
        assert response.status_code == 422
        
        # Test unsupported language pair
        unsupported_pair = None
        for src in self.available_languages:
            for tgt in self.available_languages:
                if f"{src}-{tgt}" not in SUPPORTED_MODELS:
                    unsupported_pair = (src, tgt)
                    break
            if unsupported_pair:
                break
                
        response = self.client.post("translations/translate", json={
            "text": "Hello",
            "source_lang": unsupported_pair[0],
            "target_lang": unsupported_pair[1]
        })
        assert response.status_code == 422

    def test_text_length_validation(self):
        """Test validation of text length constraints."""
        source_lang, target_lang = random.choice(list(SUPPORTED_MODELS.keys())).split('-')
        
        # Test text exceeding character limit (500 characters)
        long_text = "a" * 501  # Create text with 501 characters
        response = self.client.post("translations/translate", json={
            "text": long_text,
            "source_lang": source_lang,
            "target_lang": target_lang
        })
        assert response.status_code == 422
        assert "ensure this value has at most 500 characters" in response.json()["detail"][0]["msg"].lower()
        
        # Test text exceeding word limit (10 words)
        too_many_words = "This is a text with more than ten words to test the word limit validation"
        response = self.client.post("translations/translate", json={
            "text": too_many_words,
            "source_lang": source_lang,
            "target_lang": target_lang
        })
        assert response.status_code == 422
        assert "exceeds maximum length of 10 words" in response.json()["detail"][0]["msg"].lower()
    
    @patch('app.main.translation_service')
    def test_translate_errors(self, mock_service):
        """Test translation error handling."""
        # Get a valid language pair
        source_lang, target_lang = random.choice(list(SUPPORTED_MODELS.keys())).split('-')
        
        # Test word limit
        mock_service.translate.side_effect = ValueError("Text exceeds maximum length")
        response = self.client.post("translations/translate", json={
            "text": "This is a very long text that exceeds the limit",
            "source_lang": source_lang,
            "target_lang": target_lang
        })
        assert response.status_code == 400
        
        # Test service error
        mock_service.translate.side_effect = TranslationError("Translation failed")
        response = self.client.post("translations/translate", json={
            "text": "Hello",
            "source_lang": source_lang,
            "target_lang": target_lang
        })
        assert response.status_code == 500
    
    @patch('app.main.translation_service')
    def test_supported_languages(self, mock_service):
        """Test supported languages endpoint."""
        # Create random supported language pairs
        random_pairs = dict(random.sample(SUPPORTED_MODELS.items(), k=len(SUPPORTED_MODELS)))
        mock_service.get_supported_language_pairs.return_value = random_pairs
        
        response = self.client.get("/supported-languages")
        assert response.status_code == 200
        data = response.json()
        assert "supported_language_pairs" in data