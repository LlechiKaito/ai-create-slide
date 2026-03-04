import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

from backend.src.application.errors.application_error import ApplicationError
from backend.src.config.settings import get_cors_origins
from backend.src.domain.errors.domain_error import DomainError
from backend.src.presentation.errors.error_handler import (
    application_error_handler,
    domain_error_handler,
    generic_error_handler,
)
from backend.src.presentation.routes.slide.slide_routes import create_slide_router


def create_app() -> FastAPI:
    app = FastAPI(title="AI Slide Generator", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(ApplicationError, application_error_handler)
    app.add_exception_handler(Exception, generic_error_handler)

    app.include_router(create_slide_router())

    @app.get("/api/health")
    def health_check() -> dict:
        return {"is_success": True, "message": "OK"}

    return app


app = create_app()
