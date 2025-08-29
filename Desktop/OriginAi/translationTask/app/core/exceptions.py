"""
Generic exception handlers for FastAPI applications.
Provides centralized error handling with proper HTTP status codes and logging.
"""

import logging
from typing import Union
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError


logger = logging.getLogger(__name__)


class APIException(Exception):
    """Base exception class for API-specific errors."""
    
    def __init__(self, message: str, status_code: int = 500, detail: str = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        super().__init__(self.message)


class ValidationException(APIException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, detail: str = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, detail)


class BusinessLogicException(APIException):
    """Exception for business logic errors."""
    
    def __init__(self, message: str, detail: str = None):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY, detail)


class ServiceUnavailableException(APIException):
    """Exception for service unavailability."""
    
    def __init__(self, message: str = "Service temporarily unavailable", detail: str = None):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE, detail)


def create_error_response(
    status_code: int,
    error_type: str,
    message: str,
    detail: str = None,
    include_timestamp: bool = True
) -> JSONResponse:
    """
    Create a standardized error response.
    
    Args:
        status_code: HTTP status code
        error_type: Type of error (e.g., "Validation Error", "Internal Error")
        message: Main error message
        detail: Additional error details
        include_timestamp: Whether to include timestamp in response
    
    Returns:
        JSONResponse with standardized error format
    """
    content = {
        "error": error_type,
        "message": message
    }
    
    if detail:
        content["detail"] = detail
    
    if include_timestamp:
        from datetime import datetime
        content["timestamp"] = datetime.utcnow().isoformat() + "Z"
    
    return JSONResponse(status_code=status_code, content=content)


async def validation_exception_handler(request: Request, exc: Union[ValueError, ValidationError]) -> JSONResponse:
    """
    Handle validation errors (ValueError, Pydantic ValidationError).
    
    Args:
        request: The FastAPI request object
        exc: The validation exception
    
    Returns:
        JSONResponse with 400 status code and error details
    """
    error_message = str(exc)
    
    # Handle Pydantic ValidationError differently
    if isinstance(exc, ValidationError):
        error_message = "Request validation failed"
        detail = "; ".join([f"{'.'.join(map(str, error['loc']))}: {error['msg']}" for error in exc.errors()])
    else:
        detail = error_message
    
    logger.warning(f"Validation error on {request.url}: {error_message}")
    
    return create_error_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        error_type="Validation Error",
        message=error_message,
        detail=detail
    )


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """
    Handle custom API exceptions.
    
    Args:
        request: The FastAPI request object
        exc: The API exception
    
    Returns:
        JSONResponse with appropriate status code and error details
    """
    logger.warning(f"API exception on {request.url}: {exc.message}")
    
    return create_error_response(
        status_code=exc.status_code,
        error_type=type(exc).__name__.replace("Exception", " Error"),
        message=exc.message,
        detail=exc.detail if exc.detail != exc.message else None
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle FastAPI HTTPExceptions.
    
    Args:
        request: The FastAPI request object
        exc: The HTTP exception
    
    Returns:
        JSONResponse with standardized error format
    """
    logger.warning(f"HTTP exception on {request.url}: {exc.detail}")
    
    # Map status codes to error types
    error_type_mapping = {
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden", 
        404: "Not Found",
        422: "Unprocessable Entity",
        500: "Internal Server Error",
        503: "Service Unavailable"
    }
    
    error_type = error_type_mapping.get(exc.status_code, "HTTP Error")
    
    return create_error_response(
        status_code=exc.status_code,
        error_type=error_type,
        message=exc.detail,
        detail=None
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all other unexpected exceptions.
    
    Args:
        request: The FastAPI request object
        exc: The unexpected exception
    
    Returns:
        JSONResponse with 500 status code and generic error message
    """
    # Log the full error for debugging
    logger.error(f"Unexpected error on {request.url}: {type(exc).__name__}: {str(exc)}", exc_info=True)
    
    # Don't expose internal error details to users in production
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_type="Internal Server Error",
        message="An unexpected error occurred",
        detail="Please contact support if the problem persists"
    )


def register_exception_handlers(app) -> None:
    """
    Register all exception handlers with the FastAPI app.
    
    Args:
        app: The FastAPI application instance
    """
    # Custom API exceptions
    app.add_exception_handler(APIException, api_exception_handler)
    
    # Validation errors
    app.add_exception_handler(ValueError, validation_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    
    # FastAPI HTTP exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)
    
    # Catch-all for unexpected errors
    app.add_exception_handler(Exception, general_exception_handler)
    
    logger.info("Exception handlers registered successfully")