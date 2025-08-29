"""
Unit tests for the translation service.
"""

import pytest
from unittest.mock import Mock, patch
from app.services.translation_service import TranslationService


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
        """Test getting supported language pairs."""
        pairs = self.service.get_supported_language_pairs()
        
        expected_pairs = ["he-ru", "ru-he", "en-he", "he-en"]
        assert all(pair in pairs for pair in expected_pairs)
        assert len(pairs) == 4
    
    def test_is_model_loaded_false(self):
        """Test checking if model is loaded when not loaded."""
        assert not self.service.is_model_loaded("he-ru")
    
    @patch('app.services.translation_service.MarianTokenizer')
    @patch('app.services.translation_service.MarianMTModel')
    def test_load_model_success(self, mock_model_class, mock_tokenizer_class):
        """Test successful model loading."""
        # Setup mocks
        mock_tokenizer = Mock()
        mock_model = Mock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        mock_model_class.from_pretrained.return_value = mock_model
        
        # Test loading
        self.service._load_model("he-ru")
        
        # Verify model was loaded and cached
        assert "he-ru" in self.service._models
        assert "he-ru" in self.service._tokenizers
        assert self.service.is_model_loaded("he-ru")
    
    def test_load_model_unsupported_pair(self):
        """Test loading unsupported language pair."""
        with pytest.raises(ValueError, match="Unsupported language pair"):
            self.service._load_model("unsupported-pair")
    
    def test_translate_basic_validation(self):
        """Test basic validation without actual model loading."""
        # Test that the method validates input properly
        with pytest.raises(ValueError, match="Text cannot be empty"):
            self.service.translate("", "en", "he")
        
        with pytest.raises(ValueError, match="Unsupported language pair"):
            self.service.translate("Hello", "en", "fr")
    
    def test_translate_empty_text(self):
        """Test translation with empty text."""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            self.service.translate("", "en", "he")
    
    def test_translate_whitespace_only(self):
        """Test translation with whitespace-only text."""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            self.service.translate("   ", "en", "he")
    
    def test_translate_unsupported_pair(self):
        """Test translation with unsupported language pair."""
        with pytest.raises(ValueError, match="Unsupported language pair"):
            self.service.translate("Hello", "en", "fr")
    
    def test_translate_word_limit_exceeded(self):
        """Test translation with text exceeding 10 word limit."""
        long_text = "This is a very long text that definitely exceeds the maximum limit of ten words allowed"
        with pytest.raises(ValueError, match="Text exceeds maximum length of 10 words"):
            self.service.translate(long_text, "en", "he")
    
    @patch('app.services.translation_service.MarianTokenizer')
    @patch('app.services.translation_service.MarianMTModel')
    def test_translate_model_loading_error(self, mock_model_class, mock_tokenizer_class):
        """Test translation when model loading fails."""
        # Setup mock to raise exception
        mock_tokenizer_class.from_pretrained.side_effect = Exception("Model not found")
        
        with pytest.raises(Exception, match="Model loading failed"):
            self.service.translate("Hello", "en", "he")
    
    def test_language_code_normalization(self):
        """Test that language codes are properly normalized."""
        # This test requires mocking since we can't load actual models
        with patch.object(self.service, '_load_model') as mock_load:
            with patch.object(self.service, '_models', {"en-he": Mock()}):
                with patch.object(self.service, '_tokenizers', {"en-he": Mock()}):
                    mock_tokenizer = self.service._tokenizers["en-he"]
                    mock_model = self.service._models["en-he"]
                    
                    # Setup mock returns
                    mock_tokenizer.return_value = {"input_ids": Mock(), "attention_mask": Mock()}
                    mock_tokenizer.decode.return_value = "result"
                    mock_model.generate.return_value = [Mock()]
                    
                    # Test with uppercase and whitespace
                    self.service.translate("Hello", " EN ", " HE ")
                    
                    # Verify model was loaded with normalized pair
                    mock_load.assert_called_with("en-he")