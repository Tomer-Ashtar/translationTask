"""
Translation routes for the FastAPI application.
"""

import logging
from fastapi import APIRouter, Depends

from app.core.exceptions import ServiceNotAvailableError, TranslationError
from app.models.schemas import TranslationRequest, TranslationResponse
from app.services.translation_service import TranslationService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/translate",
    tags=["translation"]
)


def get_translation_service() -> TranslationService:
    """Dependency to get translation service instance."""
    if not hasattr(get_translation_service, 'service'):
        get_translation_service.service = TranslationService()
    return get_translation_service.service


@router.post("", response_model=TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    translation_service: TranslationService = Depends(get_translation_service)
):
    """
    Translate text from source language to target language.
    
    Args:
        request: Translation request containing text and language codes
        translation_service: Translation service instance (injected)
    
    Returns:
        Translation response with translated text
    
    Raises:
        ValueError: If validation fails
        TranslationError: If translation fails
    """
    if not translation_service:
        raise ServiceNotAvailableError("Translation service not initialized")
    
    try:
        translated_text = translation_service.translate(
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
        
        return TranslationResponse(
            translated_text=translated_text,
            source_lang=request.source_lang,
            target_lang=request.target_lang,
            original_text=request.text
        )
        
    except ValueError as e:
        raise  # Re-raise ValueError to be handled by our validation_error_handler
    except TranslationError:
        raise  # Re-raise TranslationError to be handled by our exception handler
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise TranslationError("Translation failed")