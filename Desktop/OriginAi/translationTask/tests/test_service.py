"""
Test service for testing the API without loading real models.
"""

from app.services.translation_service import TranslationService


class TestTranslationService(TranslationService):
    """Test service that doesn't load real models."""

    def __init__(self, translate_func=None, get_pairs_func=None):
        """Initialize with optional test functions."""
        super().__init__()
        self._translate_func = translate_func
        self._get_pairs_func = get_pairs_func

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Override translate to use test function."""
        if self._translate_func:
            return self._translate_func(text, source_lang, target_lang)
        return f"Translated: {text}"

    def get_supported_language_pairs(self) -> dict:
        """Override to use test function."""
        if self._get_pairs_func:
            return self._get_pairs_func()
        return {"he-ru": "test", "ru-he": "test", "en-he": "test"}