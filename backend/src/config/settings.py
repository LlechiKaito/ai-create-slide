import os

from backend.src.constants.http import CORS_ALLOWED_ORIGINS_DEFAULT


def get_cors_origins() -> list[str]:
    origins = os.environ.get("CORS_ALLOWED_ORIGINS")
    if origins:
        return [o.strip() for o in origins.split(",")]
    return CORS_ALLOWED_ORIGINS_DEFAULT


def get_host() -> str:
    host = os.environ.get("HOST")
    if not host:
        return "0.0.0.0"
    return host


def get_port() -> int:
    port = os.environ.get("PORT")
    if not port:
        return 8000
    return int(port)
