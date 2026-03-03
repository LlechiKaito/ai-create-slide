from fastapi import Request
from fastapi.responses import JSONResponse

from backend.src.application.errors.application_error import ApplicationError
from backend.src.constants.http import HttpStatus
from backend.src.domain.errors.domain_error import DomainError


async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(
        status_code=HttpStatus.BAD_REQUEST,
        content={
            "is_success": False,
            "message": exc.message,
            "code": exc.code,
        },
    )


async def application_error_handler(
    _request: Request, exc: ApplicationError
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status,
        content={
            "is_success": False,
            "message": exc.message,
            "code": exc.code,
        },
    )


async def generic_error_handler(
    _request: Request, _exc: Exception
) -> JSONResponse:
    return JSONResponse(
        status_code=HttpStatus.INTERNAL_SERVER_ERROR,
        content={
            "is_success": False,
            "message": "Internal server error",
            "code": "INTERNAL_SERVER_ERROR",
        },
    )
