"""
Simple exception handlers for FastAPI applications.
Provides centralized error handling with proper HTTP status codes.
"""

import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse


class ServiceNotAvailableError(ValueError):
    """Raised when a required service is not available."""
    pass


class TranslationError(Exception):
    """Raised when translation fails."""
    pass


logger = logging.getLogger(__name__)


async def validation_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle validation errors (ValueError from our business logic)."""
    if isinstance(exc, ServiceNotAvailableError):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        error_type = "Service Unavailable"
    else:
        status_code = status.HTTP_400_BAD_REQUEST
        error_type = "Validation Error"
    
    logger.warning(f"{error_type}: {str(exc)}")
    return JSONResponse(
        status_code=status_code,
        content={"error": error_type, "detail": str(exc)}
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other unexpected exceptions."""
    if isinstance(exc, TranslationError):
        logger.error(f"Translation error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Translation Error", "detail": str(exc)}
        )
    
    logger.error(f"Unexpected error: {type(exc).__name__}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal Server Error", "detail": "An unexpected error occurred"}
    )


async def translation_error_handler(request: Request, exc: TranslationError) -> JSONResponse:
    """Handle translation-specific errors."""
    logger.error(f"Translation error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Translation Error", "detail": str(exc)}
    )


def register_exception_handlers(app) -> None:
    """Register exception handlers with the FastAPI app."""
    app.add_exception_handler(ValueError, validation_error_handler)
    app.add_exception_handler(TranslationError, translation_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    logger.info("Exception handlers registered")