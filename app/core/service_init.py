"""
Service initialization and dependency injection module.
"""
import os
from app.services.translation_service import TranslationService

# Initialize translation service
LAZY_LOADING = os.getenv('TRANSLATION_LAZY_LOADING', 'false').lower() == 'true'
translation_service = TranslationService(lazy_loading=LAZY_LOADING)

def get_translation_service() -> TranslationService:
    """Get the singleton instance of TranslationService."""
    return translation_service