"""
Translation service using HelsinkiNLP MarianMT models from HuggingFace.
Supports Hebrew-Russian and English-Hebrew translation pairs.
"""

import logging
from typing import Dict, Optional
from transformers import MarianMTModel, MarianTokenizer
import torch

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Service for handling text translation using pre-trained MarianMT models.
    """

    
    # Model mappings for supported language pairs
    MODEL_MAPPING = {
        "he-ru": "Helsinki-NLP/opus-mt-he-ru",
        "ru-he": "Helsinki-NLP/opus-mt-ru-he", 
        "en-he": "Helsinki-NLP/opus-mt-en-he",
        "he-en": "Helsinki-NLP/opus-mt-he-en"
    }
    
    def __init__(self):
        """Initialize the translation service with empty model cache."""
        self._models: Dict[str, MarianMTModel] = {}
        self._tokenizers: Dict[str, MarianTokenizer] = {}
        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Translation service initialized with device: {self._device}")
    
    def _load_model(self, language_pair: str) -> None:
        """
        Load and cache a translation model for the given language pair.
        
        Args:
            language_pair: Language pair in format 'source-target' (e.g., 'he-ru')
        
        Raises:
            ValueError: If language pair is not supported
            Exception: If model loading fails
        """
        if language_pair in self._models:
            return
            
        if language_pair not in self.MODEL_MAPPING:
            raise ValueError(f"Unsupported language pair: {language_pair}")
        
        model_name = self.MODEL_MAPPING[language_pair]
        
        try:
            logger.info(f"Loading model for {language_pair}: {model_name}")
            
            # Load tokenizer and model
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)
            
            # Move model to appropriate device
            model = model.to(self._device)
            model.eval()  # Set to evaluation mode
            
            # Cache the loaded components
            self._tokenizers[language_pair] = tokenizer
            self._models[language_pair] = model
            
            logger.info(f"Successfully loaded model for {language_pair}")
            
        except Exception as e:
            logger.error(f"Failed to load model for {language_pair}: {str(e)}")
            raise Exception(f"Model loading failed: {str(e)}")
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text from source language to target language.
        
        Args:
            text: Text to translate
            source_lang: Source language code (he, ru, en)
            target_lang: Target language code (he, ru, en)
        
        Returns:
            Translated text
        
        Raises:
            ValueError: If language pair is not supported or text is empty
            Exception: If translation fails
        """
        # Business validation
        text = text.strip()
        if not text:
            raise ValueError("Text cannot be empty")

        word_count = len(text.split())
        if word_count > 10:
            raise ValueError(f"Text exceeds maximum length of 10 words. Current text has {word_count} words.")
        
        # Normalize language codes and create language pair
        source_lang = source_lang.lower().strip()
        target_lang = target_lang.lower().strip()
        language_pair = f"{source_lang}-{target_lang}"
        
        # Validate language pair
        if language_pair not in self.MODEL_MAPPING:
            raise ValueError(
                f"Unsupported language pair: {source_lang} -> {target_lang}. "
                f"Supported pairs: {list(self.MODEL_MAPPING.keys())}"
            )
        
        try:
            # Load model if not already cached
            self._load_model(language_pair)
            
            # Get model and tokenizer
            model = self._models[language_pair]
            tokenizer = self._tokenizers[language_pair]
            
            # Tokenize input text
            inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            
            # Generate translation
            with torch.no_grad():
                outputs = model.generate(**inputs, max_length=512, num_beams=4, early_stopping=True)
            
            # Decode the translation
            translated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            logger.info(f"Successfully translated text from {source_lang} to {target_lang}")
            return translated_text.strip()
            
        except Exception as e:
            logger.error(f"Translation failed for {language_pair}: {str(e)}")
            raise Exception(f"Translation failed: {str(e)}")
    
    def get_supported_language_pairs(self) -> Dict[str, str]:
        """
        Get all supported language pairs with their model names.
        
        Returns:
            Dictionary mapping language pairs to model names
        """
        return self.MODEL_MAPPING.copy()
    
    def is_model_loaded(self, language_pair: str) -> bool:
        """
        Check if a model is already loaded for the given language pair.
        
        Args:
            language_pair: Language pair in format 'source-target'
        
        Returns:
            True if model is loaded, False otherwise
        """
        return language_pair in self._models