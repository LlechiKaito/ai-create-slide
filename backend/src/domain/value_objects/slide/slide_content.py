from dataclasses import dataclass

from backend.src.constants.slide import MAX_CONTENT_LENGTH
from backend.src.domain.errors.domain_error import DOMAIN_ERRORS, DomainError


@dataclass(frozen=True)
class SlideContent:
    value: str

    def __post_init__(self) -> None:
        if len(self.value) > MAX_CONTENT_LENGTH:
            raise DomainError(**DOMAIN_ERRORS["CONTENT_TOO_LONG"])
