class DomainError(Exception):
    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.message = message
        self.code = code


DOMAIN_ERRORS = {
    "EMPTY_TITLE": {
        "message": "Slide title cannot be empty",
        "code": "EMPTY_TITLE",
    },
    "TITLE_TOO_LONG": {
        "message": "Slide title exceeds maximum length",
        "code": "TITLE_TOO_LONG",
    },
    "EMPTY_SLIDES": {
        "message": "Slide deck must contain at least one slide",
        "code": "EMPTY_SLIDES",
    },
    "TOO_MANY_SLIDES": {
        "message": "Slide deck exceeds maximum number of slides",
        "code": "TOO_MANY_SLIDES",
    },
    "CONTENT_TOO_LONG": {
        "message": "Slide content exceeds maximum length",
        "code": "CONTENT_TOO_LONG",
    },
}
