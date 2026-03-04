import os

import boto3

from backend.src.constants.aws import GEMINI_API_KEY_MISSING_ERROR, SSM_PARAM_NAME_ENV_KEY
from backend.src.constants.http import CORS_ALLOWED_ORIGINS_DEFAULT

_gemini_api_key_cache: str | None = None


def get_gemini_api_key() -> str:
    global _gemini_api_key_cache
    if _gemini_api_key_cache:
        return _gemini_api_key_cache

    local_key = os.environ.get("GEMINI_API_KEY")
    if local_key and local_key != "your_api_key_here":
        _gemini_api_key_cache = local_key
        return _gemini_api_key_cache

    ssm_param_name = os.environ.get(SSM_PARAM_NAME_ENV_KEY)
    if not ssm_param_name:
        raise RuntimeError(GEMINI_API_KEY_MISSING_ERROR)

    ssm = boto3.client("ssm")
    response = ssm.get_parameter(Name=ssm_param_name, WithDecryption=True)
    _gemini_api_key_cache = response["Parameter"]["Value"]
    return _gemini_api_key_cache


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
