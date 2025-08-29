"""
Translation and language routes for the FastAPI application.
"""

import logging
from fastapi import APIRouter, Depends

from app.core.exceptions import ServiceNotAvailableError, TranslationError
from app.models.schemas import TranslationRequest, TranslationResponse
from app.services.translation_service import TranslationService
from app.core.translation_config import LANGUAGE_CODES, get_supported_language_pairs

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/translations",
    tags=["translation"]
)

translation_service_dependency = Depends(lambda: get_translation_service())

def get_translation_service() -> TranslationService:
    if not hasattr(get_translation_service, 'service'):
        get_translation_service.service = TranslationService()
    
    service = get_translation_service.service
    if not service:
        raise ServiceNotAvailableError("Translation service not initialized")
    
    return service


@router.post("/translate", response_model = TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    translation_service: TranslationService = translation_service_dependency
):
    
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
    
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise TranslationError("Translation failed")


@router.get("/supported_languages", response_model=dict)
def get_supported_languages():
    return {
        "supported_language_pairs": get_supported_language_pairs(),
        "language_codes": LANGUAGE_CODES
    }