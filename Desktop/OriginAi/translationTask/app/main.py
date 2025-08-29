"""
FastAPI application for translation service.
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from app.services.translation_service import TranslationService
from app.core.exceptions import (
    register_exception_handlers,
    ServiceNotAvailableError,
    TranslationError
)
from app.models.schemas import (
    TranslationRequest,
    TranslationResponse,
    BatchTranslationRequest,
    BatchTranslationResponse,
    HealthResponse
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s  %(message)s"
)
logger = logging.getLogger(__name__)

# Global translation service instance
translation_service: Optional[TranslationService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events."""
    global translation_service
    
    # Startup
    logger.info("Starting Translation service...")
    translation_service = TranslationService()
    logger.info("Translation service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Translation service...")


# Create FastAPI app
app = FastAPI(
    title="Translation Service",
    description="REST API for text translation using HelsinkiNLP MarianMT models",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for web browser compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all exception handlers
register_exception_handlers(app)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    if translation_service is None:
        raise ServiceNotAvailableError("Translation service not initialized")
    
    supported_pairs = list(translation_service.get_supported_language_pairs().keys())
    loaded_models = [
        pair for pair in supported_pairs 
        if translation_service.is_model_loaded(pair)
    ]
    
    return HealthResponse(
        status="healthy",
        supported_language_pairs=supported_pairs,
        loaded_models=loaded_models
    )


@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate a single text from source language to target language.
    
    Args:
        request: Translation request containing text and language codes
    
    Returns:
        Translation response with translated text
    
    Raises:
        HTTPException: If translation fails or service unavailable
    """
    if translation_service is None:
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
    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise TranslationError("Translation failed")


@app.post("/translate/batch", response_model=BatchTranslationResponse)
async def translate_batch(request: BatchTranslationRequest):
    """
    Translate multiple texts from source language to target language.
    
    Args:
        request: Batch translation request containing texts and language codes
    
    Returns:
        Batch translation response with all translated texts
    
    Raises:
        HTTPException: If translation fails or service unavailable
    """
    if translation_service is None:
        raise ServiceNotAvailableError("Translation service not initialized")
    
    try:
        translations = []
        
        for text in request.texts:
            translated_text = translation_service.translate(
                text=text,
                source_lang=request.source_lang,
                target_lang=request.target_lang
            )
            
            translations.append(TranslationResponse(
                translated_text=translated_text,
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                original_text=text
            ))
        
        return BatchTranslationResponse(
            translations=translations,
            total_count=len(translations)
        )
        
    except ValueError as e:
        raise  # Re-raise ValueError to be handled by our validation_error_handler
    except Exception as e:
        logger.error(f"Batch translation error: {str(e)}")
        raise TranslationError("Batch translation failed")


@app.get("/supported-languages", response_model=dict)
async def get_supported_languages():
    """Get information about supported language pairs."""
    if translation_service is None:
        raise ServiceNotAvailableError("Translation service not initialized")
    
    return {
        "supported_language_pairs": translation_service.get_supported_language_pairs(),
        "language_codes": {
            "he": "Hebrew",
            "ru": "Russian", 
            "en": "English"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)