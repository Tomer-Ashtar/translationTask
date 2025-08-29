"""
Translation and language routes for the FastAPI application.
"""

import logging
from fastapi import APIRouter, Depends

from app.core.exceptions import TranslationError, TranslationFailedError
from app.models.schemas import TranslationRequest, TranslationResponse
from app.services.translation_service import TranslationService
from app.core.translation_config import LANGUAGE_CODES, get_supported_language_pairs

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/translations",
    tags=["translation"]
)

from app.core.service_init import get_translation_service

translation_service_dependency = Depends(get_translation_service)


@router.post("/translate", response_model = TranslationResponse)
async def translate_text(
    request: TranslationRequest,
    translation_service: TranslationService = translation_service_dependency
):
    
    try:
        translated_text = translation_service.translate(
            text = request.text,
            source_lang = request.source_lang,
            target_lang = request.target_lang
        )
        
        return TranslationResponse(
            translated_text = translated_text,
            source_lang = request.source_lang,
            target_lang = request.target_lang,
            original_text = request.text
        )
    
    except TranslationError:
        # Just re-raise any TranslationError (including ServiceNotAvailableError) as is
        # This preserves the original error message and type
        raise
    except Exception as e:
        # Wrap any other unexpected error in TranslationFailedError
        logger.error(f"Unexpected translation error: {str(e)}")
        raise TranslationFailedError("Translation failed due to an unexpected error")


@router.get("/supported-languages", response_model = dict)
def get_supported_languages():
    return {
        "supported_language_pairs": get_supported_language_pairs(),
        "language_codes": LANGUAGE_CODES
    }