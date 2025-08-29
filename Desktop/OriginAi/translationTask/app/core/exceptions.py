"""
Simple exception handlers for FastAPI applications.
Provides centralized error handling with proper HTTP status codes.
"""

import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse


logger = logging.getLogger(__name__)


async def validation_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Handle validation errors (ValueError from our business logic)."""
    logger.warning(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Validation Error", "detail": str(exc)}
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other unexpected exceptions."""
    logger.error(f"Unexpected error: {type(exc).__name__}: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal Server Error", "detail": "An unexpected error occurred"}
    )


def register_exception_handlers(app) -> None:
    """Register exception handlers with the FastAPI app."""
    app.add_exception_handler(ValueError, validation_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    logger.info("Exception handlers registered")