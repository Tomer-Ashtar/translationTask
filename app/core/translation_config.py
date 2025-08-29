"""
Configuration file for translation-related constants and mappings.
"""
from typing import Dict

# Mapping of language codes to their full names
LANGUAGE_CODES = {
    "he": "Hebrew",
    "ru": "Russian",
    "en": "English"
}

# Mapping of supported language pairs to their respective models
SUPPORTED_MODELS = {
    "he-ru": "Helsinki-NLP/opus-mt-he-ru",
    "en-he": "Helsinki-NLP/opus-mt-en-he",
}

def get_supported_language_pairs() -> Dict[str, str]:
    """
    Get all supported language pairs with their model names.
    
    Returns:
        Dictionary mapping language pairs to model names
    """
    return SUPPORTED_MODELS.copy() 