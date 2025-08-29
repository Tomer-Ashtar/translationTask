"""
Pydantic models for request and response validation.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class TranslationRequest(BaseModel):
    """Request model for translation endpoint."""
    
    text: str = Field(
        ..., 
        min_length=1,  # Basic structural validation
        max_length=500,  # Technical limit
        description="Text to translate"
    )
    source_lang: str = Field(..., description="Source language code (he, ru, en)")
    target_lang: str = Field(..., description="Target language code (he, ru, en)")
    
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
        allowed_langs = {'he', 'ru', 'en'}
        v = v.lower().strip()
        if v not in allowed_langs:
            raise ValueError(f"Language code must be one of: {allowed_langs}")
        return v
    
    @field_validator('target_lang')
    @classmethod
    def validate_different_languages(cls, v, info):
        """Ensure source and target languages are different."""
        if info.data.get('source_lang') and v == info.data['source_lang']:
            raise ValueError("Source and target languages must be different")
        return v





class TranslationResponse(BaseModel):
    """Response model for translation endpoint."""
    
    translated_text: str = Field(..., description="The translated text")
    source_lang: str = Field(..., description="Source language code")
    target_lang: str = Field(..., description="Target language code")
    original_text: str = Field(..., description="Original input text")







class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")


