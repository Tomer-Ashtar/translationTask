"""
Translation service using HelsinkiNLP MarianMT models from HuggingFace.
Supports Hebrew-Russian and English-Hebrew translation pairs.
"""

import logging
from typing import Dict, Optional
from transformers import MarianMTModel, MarianTokenizer
import torch
from app.core.translation_config import SUPPORTED_MODELS

logger = logging.getLogger(__name__)


class TranslationService:
    
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
            Exception: If model loading fails
        """
        if language_pair in self._models:
            return
            
        model_name = SUPPORTED_MODELS[language_pair]
        
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
        All input validation is handled by the TranslationRequest schema.
        """
        language_pair = f"{source_lang}-{target_lang}"
        
        try:
            # Load model if not already cached
            self._load_model(language_pair)
            
            # Get model and tokenizer
            model = self._models[language_pair]
            tokenizer = self._tokenizers[language_pair]
            
            # Tokenize input text
            inputs = tokenizer(text, return_tensors = "pt", padding = True, truncation = True, max_length = 512)
            inputs = {k: v.to(self._device) for k, v in inputs.items()}
            
            # Generate translation
            with torch.no_grad():
                outputs = model.generate(**inputs, max_length = 512, num_beams = 4, early_stopping = True)
            
            # Decode the translation
            translated_text = tokenizer.decode(outputs[0], skip_special_tokens = True)
            
            logger.info(f"Successfully translated text from {source_lang} to {target_lang}")
            return translated_text.strip()
            
        except Exception as e:
            logger.error(f"Translation failed for {language_pair}: {str(e)}")
            raise Exception(f"Translation failed: {str(e)}")
    