from dataclasses import dataclass

from backend.src.constants.slide import MAX_TITLE_LENGTH
from backend.src.domain.errors.domain_error import DOMAIN_ERRORS, DomainError


@dataclass(frozen=True)
class SlideTitle:
    value: str

    def __post_init__(self) -> None:
        if not self.value.strip():
            raise DomainError(**DOMAIN_ERRORS["EMPTY_TITLE"])
        if len(self.value) > MAX_TITLE_LENGTH:
            raise DomainError(**DOMAIN_ERRORS["TITLE_TOO_LONG"])
