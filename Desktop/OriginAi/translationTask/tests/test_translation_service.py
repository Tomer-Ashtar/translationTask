"""
Test cases for the TranslationService class.
"""
import pytest
from unittest.mock import Mock, patch
import random
import torch

from app.services.translation_service import TranslationService
from app.core.translation_config import SUPPORTED_MODELS, LANGUAGE_CODES

def random_lazy_loading():
    """Helper function to get random lazy_loading value."""
    return random.choice([True, False])

class TestTranslationService:
    """Test cases for TranslationService."""
    
    def test_model_loading_strategy(self):
        """Test that models are loaded according to the specified strategy (lazy vs eager)."""
        # Test lazy loading - models should be empty at init
        lazy_service = TranslationService(lazy_loading=True)
        assert len(lazy_service._models) == 0
        assert len(lazy_service._tokenizers) == 0
        
        # Test eager loading - all models should be loaded at init
        eager_service = TranslationService(lazy_loading=False)
        assert len(eager_service._models) == len(SUPPORTED_MODELS)
        assert len(eager_service._tokenizers) == len(SUPPORTED_MODELS)

    @patch('app.services.translation_service.MarianMTModel')
    @patch('app.services.translation_service.MarianTokenizer')
    def test_translation_with_random_language_pair(self, mock_tokenizer_class, mock_model_class):
        """Test translation with random supported language pairs."""
        mock_tokenizer = Mock()
        mock_model = Mock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        mock_model_class.from_pretrained.return_value = mock_model
        mock_model.to.return_value = mock_model
        
        language_pair = random.choice(list(SUPPORTED_MODELS.keys()))
        source_lang, target_lang = language_pair.split('-')
        
        expected_translation = "מתורגם" if target_lang == "he" else "переведенный" if target_lang == "ru" else "translated"
        
        # Mock the tokenizer to return a proper dictionary with tensor-like objects
        mock_input_ids = Mock()
        mock_attention_mask = Mock()
        mock_input_ids.to = Mock(return_value=mock_input_ids)
        mock_attention_mask.to = Mock(return_value=mock_attention_mask)
        mock_tokenizer.side_effect = lambda *args, **kwargs: {"input_ids": mock_input_ids, "attention_mask": mock_attention_mask}
        
        # Mock model generation and tokenizer decode
        mock_output = Mock()
        mock_model.generate.return_value = [mock_output]
        mock_tokenizer.decode.return_value = expected_translation
        
        service = TranslationService(lazy_loading=random_lazy_loading())
        result = service.translate("Test text", source_lang, target_lang)
        
        assert result == expected_translation
        assert mock_model.generate.called
        assert mock_tokenizer.decode.called

    @patch('app.services.translation_service.MarianMTModel')
    @patch('app.services.translation_service.MarianTokenizer')
    def test_model_caching_and_reuse(self, mock_tokenizer_class, mock_model_class):
        """Test that models are properly cached and reused."""
        mock_tokenizer = Mock()
        mock_model = Mock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        mock_model_class.from_pretrained.return_value = mock_model
        mock_model.to.return_value = mock_model
        
        language_pair = random.choice(list(SUPPORTED_MODELS.keys()))
        source_lang, target_lang = language_pair.split('-')
        
        # Mock the tokenizer to return a proper dictionary with tensor-like objects
        mock_input_ids = Mock()
        mock_attention_mask = Mock()
        mock_input_ids.to = Mock(return_value=mock_input_ids)
        mock_attention_mask.to = Mock(return_value=mock_attention_mask)
        mock_tokenizer.side_effect = lambda *args, **kwargs: {"input_ids": mock_input_ids, "attention_mask": mock_attention_mask}
        
        # Mock model generation
        mock_output = Mock()
        mock_model.generate.return_value = [mock_output]
        mock_tokenizer.decode.return_value = "Test translation"
        
        service = TranslationService(lazy_loading=random_lazy_loading())
        
        service.translate("First text", source_lang, target_lang)
        first_load_calls = mock_model_class.from_pretrained.call_count
        
        service.translate("Second text", source_lang, target_lang)
        second_load_calls = mock_model_class.from_pretrained.call_count
        
        assert second_load_calls == first_load_calls
        assert language_pair in service._models
        assert language_pair in service._tokenizers

    @patch('app.services.translation_service.MarianMTModel')
    @patch('app.services.translation_service.MarianTokenizer')
    def test_translation_error_handling(self, mock_tokenizer_class, mock_model_class):
        """Test that translation errors are properly handled and re-raised."""
        mock_tokenizer = Mock()
        mock_model = Mock()
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
        mock_model_class.from_pretrained.return_value = mock_model
        mock_model.to.return_value = mock_model
        
        language_pair = random.choice(list(SUPPORTED_MODELS.keys()))
        source_lang, target_lang = language_pair.split('-')
        
        # Mock the tokenizer to return a proper dictionary with tensor-like objects
        mock_input_ids = Mock()
        mock_attention_mask = Mock()
        mock_input_ids.to = Mock(return_value=mock_input_ids)
        mock_attention_mask.to = Mock(return_value=mock_attention_mask)
        mock_tokenizer.side_effect = lambda *args, **kwargs: {"input_ids": mock_input_ids, "attention_mask": mock_attention_mask}
        
        # Setup mock to raise exception during translation
        mock_model.generate.side_effect = Exception("Model generation failed")
        
        service = TranslationService(lazy_loading=random_lazy_loading())
        
        with pytest.raises(Exception) as exc_info:
            service.translate("Test text", source_lang, target_lang)
        
        assert "Translation failed" in str(exc_info.value)
        assert "Model generation failed" in str(exc_info.value)
