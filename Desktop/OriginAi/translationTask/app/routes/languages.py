"""
Language information routes for the FastAPI application.
"""

from fastapi import APIRouter, Depends

from app.core.exceptions import ServiceNotAvailableError
from app.services.translation_service import TranslationService
from app.routes.translation import get_translation_service

router = APIRouter(
    prefix="/languages",
    tags=["languages"]
)


@router.get("/supported", response_model=dict)
async def get_supported_languages(
    translation_service: TranslationService = Depends(get_translation_service)
):
    """
    Get information about supported language pairs.
    
    Args:
        translation_service: Translation service instance (injected)
    
    Returns:
        Dictionary containing supported language pairs and codes
    
    Raises:
        ServiceNotAvailableError: If service is not initialized
    """
    if not translation_service:
        raise ServiceNotAvailableError("Translation service not initialized")
    
    return {
        "supported_language_pairs": translation_service.get_supported_language_pairs(),
        "language_codes": {
            "he": "Hebrew",
            "ru": "Russian", 
            "en": "English"
        }
    }