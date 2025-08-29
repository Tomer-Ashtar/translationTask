"""
Pydantic models for request and response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from app.core.translation_config import LANGUAGE_CODES, SUPPORTED_MODELS


class TranslationRequest(BaseModel):    
    text: str = Field( ..., min_length = 1, max_length = 500, description="Text to translate")
    source_lang: str = Field(..., description=f"Source language code {list(LANGUAGE_CODES.keys())}")
    target_lang: str = Field(..., description=f"Target language code {list(LANGUAGE_CODES.keys())}")
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v):
        """Validate that text is not just whitespace and doesn't exceed word limit."""
        if not v.strip():
            raise ValueError("Text cannot be empty or just whitespace")

        # Check word count limit (maximum 10 words)
        word_count = len(v.strip().split())
        if word_count > 10:
            raise ValueError(f"Text exceeds maximum length of 10 words. Current text has {word_count} words.")
        
        return v.strip()

    @field_validator('source_lang', 'target_lang')
    @classmethod
    def validate_language_codes(cls, v):
        """Validate language codes."""
        v = v.lower().strip()
        if v not in LANGUAGE_CODES:
            raise ValueError(f"Language code must be one of: {list(LANGUAGE_CODES.keys())}")
        return v
    
    @field_validator('target_lang')
    @classmethod
    def validate_language_pair(cls, target_lang, info):
        """Validate that the language pair is supported and languages are different."""
        source_lang = info.data.get('source_lang')
        if not source_lang:
            return target_lang
            
        # Check if languages are different
        if target_lang == source_lang:
            raise ValueError("Source and target languages must be different")
            
        # Check if language pair is supported
        lang_pair = f"{source_lang}-{target_lang}"
        if lang_pair not in SUPPORTED_MODELS:
            supported_pairs = list(SUPPORTED_MODELS.keys())
            raise ValueError(
                f"Unsupported language pair: {source_lang} -> {target_lang}. "
                f"Supported pairs: {supported_pairs}"
            )
            
        return target_lang


class TranslationResponse(BaseModel):
    """Response model for translation endpoint."""
    
    translated_text: str = Field(..., description = "The translated text")
    source_lang: str = Field(..., description = "Source language code")
    target_lang: str = Field(..., description = "Target language code")
    original_text: str = Field(..., description = "Original input text")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")


