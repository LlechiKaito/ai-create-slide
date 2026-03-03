from backend.src.constants.http import HttpStatus


class ApplicationError(Exception):
    def __init__(self, message: str, code: str, status: int) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status = status


class ValidationError(ApplicationError):
    def __init__(self, message: str, code: str = "VALIDATION_ERROR") -> None:
        super().__init__(message, code, HttpStatus.BAD_REQUEST)


class NotFoundError(ApplicationError):
    def __init__(self, message: str, code: str = "NOT_FOUND") -> None:
        super().__init__(message, code, HttpStatus.NOT_FOUND)


APPLICATION_ERRORS = {
    "SLIDE_GENERATION_FAILED": {
        "message": "Failed to generate slides",
        "code": "SLIDE_GENERATION_FAILED",
        "status": HttpStatus.INTERNAL_SERVER_ERROR,
    },
    "INVALID_SLIDE_DATA": {
        "message": "Invalid slide data provided",
        "code": "INVALID_SLIDE_DATA",
        "status": HttpStatus.BAD_REQUEST,
    },
}
