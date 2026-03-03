from dataclasses import dataclass
from typing import Optional

from backend.src.domain.value_objects.slide.slide_content import SlideContent
from backend.src.domain.value_objects.slide.slide_title import SlideTitle


@dataclass(frozen=True)
class Slide:
    title: SlideTitle
    content: SlideContent
    subtitle: Optional[str] = None
    bullet_points: tuple[str, ...] = ()

    def has_bullet_points(self) -> bool:
        return len(self.bullet_points) > 0
