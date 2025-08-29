"""
Unit tests for the translation service.
"""

import pytest
from unittest.mock import Mock, patch
from app.services.translation_service import TranslationService
from app.core.translation_config import get_supported_language_pairs


class TestTranslationService:
    """Test cases for TranslationService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = TranslationService()
    
    def test_initialization(self):
        """Test service initialization."""
        assert isinstance(self.service._models, dict)
        assert isinstance(self.service._tokenizers, dict)
        assert len(self.service._models) == 0
        assert len(self.service._tokenizers) == 0
    
    def test_supported_language_pairs(self):
        """Test getting supported language pairs from config."""
        pairs = get_supported_language_pairs()
        expected_pairs = {
            "he-ru": "Helsinki-NLP/opus-mt-he-ru",
            "en-he": "Helsinki-NLP/opus-mt-en-he"
        }
        assert pairs == expected_pairs
    
    @patch('app.services.translation_service.MarianTokenizer')
    @patch('app.services.translation_service.MarianMTModel')
    def test_successful_translation(self, mock_model_class, mock_tokenizer_class):
        """Test successful translation flow."""
        # Setup mocks
        mock_tokenizer = Mock()
        mock_model = Mock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        mock_model_class.from_pretrained.return_value = mock_model
        
        # Setup expected behavior
        expected_translation = "תרגום"
        mock_tokenizer.return_value = {"input_ids": Mock(), "attention_mask": Mock()}
        mock_tokenizer.decode.return_value = expected_translation
        mock_model.generate.return_value = [Mock()]
        mock_model.to.return_value = mock_model
        
        # Test translation
        with patch.object(mock_tokenizer, '__call__', return_value={"input_ids": Mock(), "attention_mask": Mock()}):
            result = self.service.translate("Hello", "en", "he")
            
        # Verify result
        assert result == expected_translation
        
        # Verify successful translation
        assert result == expected_translation
        assert mock_model.generate.called
        assert mock_tokenizer.decode.called
    
    @patch('app.services.translation_service.MarianTokenizer')
    @patch('app.services.translation_service.MarianMTModel')
    def test_translation_model_loading_error(self, mock_model_class, mock_tokenizer_class):
        """Test translation fails when model loading fails."""
        mock_tokenizer_class.from_pretrained.side_effect = Exception("Model not found")
        
        with pytest.raises(Exception, match="Model loading failed"):
            self.service.translate("Hello", "en", "he")
    
    @patch('app.services.translation_service.MarianTokenizer')
    @patch('app.services.translation_service.MarianMTModel')
    def test_translation_process_error(self, mock_model_class, mock_tokenizer_class):
        """Test translation fails when translation process fails."""
        # Setup mocks for successful loading but failed translation
        mock_tokenizer = Mock()
        mock_model = Mock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        mock_model_class.from_pretrained.return_value = mock_model
        
        # Setup translation failure
        mock_model.generate.side_effect = Exception("Translation process failed")
        mock_tokenizer.return_value = {"input_ids": Mock(), "attention_mask": Mock()}
        
        with pytest.raises(Exception, match="Translation failed"):
            self.service.translate("Hello", "en", "he")